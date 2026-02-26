import networkx as nx
import logging
import pickle
import json
from pathlib import Path

class SpiderFootGraphEngine:
    """Core graph engine for building and managing intelligence graphs from OSINT data."""

    def __init__(self, dbh, scan_id):
        """
        Initialize graph engine.
        
        Args:
            dbh: SpiderFootDb database handle
            scan_id: Scan instance ID
        """
        self.dbh = dbh
        self.scan_id = scan_id
        self.log = logging.getLogger(f"spiderfoot.{__name__}")
        self.graph = nx.MultiDiGraph()  # Directed multi-graph

    def build_graph_from_scan(self, include_affiliates=True, max_events=None):
        """
        Build NetworkX graph from scan results.
        
        Args:
            include_affiliates: Include affiliate entities
            max_events: Maximum number of events to process
            
        Returns:
            NetworkX MultiDiGraph
        """
        self.log.info(f"Building graph for scan {self.scan_id}...")
        
        # Clear existing graph
        self.graph.clear()
        
        # Query: Get all results for this scan
        query = """
            SELECT hash, type, data, source_event_hash, module, confidence
            FROM tbl_scan_results
            WHERE scan_instance_id = ?
        """
        
        if not include_affiliates:
            query += " AND type NOT LIKE '%AFFILIATE%'"
        
        if max_events:
            query += f" LIMIT {max_events}"
        
        try:
            with self.dbh.dbhLock:
                self.dbh.dbh.execute(query, (self.scan_id,))
                rows = self.dbh.dbh.fetchall()
            
            nodes = {}
            edges = []
            
            # Create ROOT node
            self.graph.add_node("ROOT", type="ROOT", label="Target", confidence=100, data="Root", color="#222")
            
            for row in rows:
                r_hash = row[0]
                r_type = row[1]
                r_data = row[2]
                r_src_hash = row[3]
                r_module = row[4]
                r_conf = row[5] if row[5] else 50
                
                # Get color for type
                color = self._get_node_color(r_type)
                
                # Store node attributes
                nodes[r_hash] = {
                    "type": r_type,
                    "label": r_data[:50] if r_data else "Unknown",
                    "data": r_data,
                    "confidence": r_conf,
                    "color": color
                }
                
                # Store edge relationship
                if r_src_hash:
                    edges.append((r_src_hash, r_hash, {"module": r_module, "type": "RELATED"}))
            
            # Add nodes to graph
            for n_id, attrs in nodes.items():
                self.graph.add_node(n_id, **attrs)
                
            # Add edges to graph
            for src, dst, attrs in edges:
                if self.graph.has_node(src) and self.graph.has_node(dst):
                    self.graph.add_edge(src, dst, **attrs)
                elif src == "ROOT" and self.graph.has_node(dst):
                    self.graph.add_edge("ROOT", dst, **attrs)
            
            self.log.info(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            return self.graph

        except Exception as e:
            self.log.error(f"Failed to build graph: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _get_node_color(self, node_type):
        """Get color for node type for visualization."""
        colors = {
            'IP_ADDRESS': '#3498db',  # Blue
            'IPV6_ADDRESS': '#2980b9',
            'DOMAIN_NAME': '#2ecc71',  # Green
            'INTERNET_NAME': '#27ae60',
            'EMAILADDR': '#e74c3c',  # Red
            'HUMAN_NAME': '#f39c12',  # Orange
            'PHONE_NUMBER': '#9b59b6',  # Purple
            'PHYSICAL_ADDRESS': '#1abc9c',  # Turquoise
            'USERNAME': '#e67e22',  # Dark orange
            'AFFILIATE': '#95a5a6',  # Gray
        }
        
        for key, color in colors.items():
            if key in node_type:
                return color
        
        return '#34495e'  # Default dark gray

    def get_graph_stats(self):
        """Get graph statistics."""
        if self.graph.number_of_nodes() == 0:
            return {
                'num_nodes': 0,
                'num_edges': 0,
                'density': 0.0,
                'num_weakly_connected_components': 0
            }
        
        # Calculate density
        n = self.graph.number_of_nodes()
        m = self.graph.number_of_edges()
        max_edges = n * (n - 1)  # For directed graph
        density = m / max_edges if max_edges > 0 else 0.0
        
        # Count components
        undirected = self.graph.to_undirected()
        num_components = nx.number_connected_components(undirected)
        
        return {
            'num_nodes': n,
            'num_edges': m,
            'density': density,
            'num_weakly_connected_components': num_components
        }

    def save_to_disk(self, filepath):
        """Save graph to disk using pickle."""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.graph, f)
            self.log.info(f"Graph saved to {filepath}")
            return filepath
        except Exception as e:
            self.log.error(f"Failed to save graph: {e}")
            return None

    def load_from_disk(self, filepath):
        """Load graph from disk."""
        try:
            with open(filepath, 'rb') as f:
                self.graph = pickle.load(f)
            self.log.info(f"Graph loaded from {filepath}")
            return self.graph
        except Exception as e:
            self.log.error(f"Failed to load graph: {e}")
            return None

    def export_graph(self, format='json', filepath=None):
        """
        Export graph in various formats.
        
        Args:
            format: Export format (json, gexf, graphml)
            filepath: Output file path
            
        Returns:
            Path to exported file
        """
        if not filepath:
            filepath = f"/tmp/graph_{self.scan_id}.{format}"
        
        try:
            if format == 'json':
                data = nx.node_link_data(self.graph)
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format == 'gexf':
                nx.write_gexf(self.graph, filepath)
            
            elif format == 'graphml':
                nx.write_graphml(self.graph, filepath)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.log.info(f"Graph exported to {filepath}")
            return filepath
        
        except Exception as e:
            self.log.error(f"Failed to export graph: {e}")
            return None
