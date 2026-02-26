import logging
import json
from spiderfoot import SpiderFootDb
from spiderfoot.graph_engine import SpiderFootGraphEngine
from spiderfoot.graph_algorithms import GraphAnalyzer

class GraphCorrelator:
    """Orchestrates graph-based correlation."""
    
    def __init__(self, config, scan_id):
        self.config = config
        self.scan_id = scan_id
        self.log = logging.getLogger(f"spiderfoot.{__name__}")
        self.dbh = SpiderFootDb(self.config)

    def run(self):
        """Run the full graph correlation pipeline."""
        self.log.info(f"Starting graph correlation for {self.scan_id}")
        
        # 1. Build Graph
        engine = SpiderFootGraphEngine(self.config)
        graph = engine.build_graph_from_scan(self.scan_id)
        
        if not graph:
            self.log.error("Graph build failed.")
            return
            
        # 2. Analyze
        analyzer = GraphAnalyzer(graph)
        communities = analyzer.detect_communities()
        centrality = analyzer.calculate_centrality()
        anomalies = analyzer.detect_anomalies()
        
        # 3. Store Results
        self.store_results("community", "louvain", communities)
        self.store_results("centrality", "pagerank", centrality)
        self.store_results("anomaly", "heuristic", anomalies)
        
        self.log.info("Graph correlation complete.")

    def store_results(self, corr_type, algo, data):
        """Store correlation results to DB."""
        
        entities_json = json.dumps(data)
        
        # Store in tbl_scan_graph_correlations
        query = """
            INSERT INTO tbl_scan_graph_correlations 
            (scan_instance_id, correlation_type, algorithm, entities, created_time)
            VALUES (?, ?, ?, ?, datetime('now'))
        """
        
        try:
            with self.dbh.dbhLock:
                self.dbh.dbh.execute(query, (self.scan_id, corr_type, algo, entities_json))
                self.dbh.conn.commit()
        except Exception as e:
            self.log.error(f"Failed to store graph correlations: {e}")
