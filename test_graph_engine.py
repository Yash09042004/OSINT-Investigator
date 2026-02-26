#!/usr/bin/env python3
"""
Test script for PRISM graph correlation engine.
Tests basic functionality of graph_engine, graph_algorithms, and graph_correlation modules.
"""

import sys
import os

# Add SpiderFoot to path
sys.path.insert(0, '/home/yash/Desktop/MEGA_PROJECT/spiderfoot')

def test_graph_engine():
    """Test graph engine basic functionality"""
    print("\n" + "="*60)
    print("TEST 1: Graph Engine Basic Functionality")
    print("="*60)
    
    try:
        from spiderfoot.graph_engine import SpiderFootGraphEngine
        from spiderfoot.db import SpiderFootDb
        import networkx as nx
        
        # Create a test database connection
        opts = {'__database': '/tmp/test_prism.db'}
        dbh = SpiderFootDb(opts, init=True)
        
        # Create a test scan instance
        scan_id = 'test_scan_123'
        dbh.scanInstanceCreate(scan_id, 'Test Scan', 'example.com')
        
        # Initialize graph engine
        engine = SpiderFootGraphEngine(dbh, scan_id)
        print("✓ Graph engine initialized successfully")
        
        # Test adding nodes
        engine.add_entity_node('node1', 'IP_ADDRESS', '192.168.1.1', {'test': True})
        engine.add_entity_node('node2', 'DOMAIN_NAME', 'example.com', {'test': True})
        engine.add_entity_node('node3', 'EMAILADDR', 'test@example.com', {'test': True})
        
        print(f"✓ Added 3 test nodes")
        print(f"  Graph has {engine.graph.number_of_nodes()} nodes")
        
        # Test adding edges
        engine.add_relationship_edge('node2', 'node1', 'DNS_RESOLUTION')
        engine.add_relationship_edge('node3', 'node2', 'RELATED')
        
        print(f"✓ Added 2 test edges")
        print(f"  Graph has {engine.graph.number_of_edges()} edges")
        
        # Test graph stats
        stats = engine.get_graph_stats()
        print(f"✓ Graph statistics retrieved:")
        print(f"  - Nodes: {stats['num_nodes']}")
        print(f"  - Edges: {stats['num_edges']}")
        print(f"  - Density: {stats['density']:.4f}")
        
        # Test export
        export_path = engine.export_graph('json', '/tmp/test_graph.json')
        print(f"✓ Graph exported to {export_path}")
        
        # Cleanup
        os.remove('/tmp/test_prism.db')
        os.remove('/tmp/test_graph.json')
        
        print("\n✅ Graph Engine Test: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Graph Engine Test: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_algorithms():
    """Test graph algorithms"""
    print("\n" + "="*60)
    print("TEST 2: Graph Algorithms")
    print("="*60)
    
    try:
        from spiderfoot.graph_algorithms import GraphAnalyzer
        import networkx as nx
        
        # Create a test graph
        G = nx.MultiDiGraph()
        
        # Add nodes (simulate a small threat network)
        nodes = [
            ('n1', {'type': 'IP_ADDRESS', 'data': '192.168.1.1'}),
            ('n2', {'type': 'DOMAIN_NAME', 'data': 'evil1.com'}),
            ('n3', {'type': 'DOMAIN_NAME', 'data': 'evil2.com'}),
            ('n4', {'type': 'IP_ADDRESS', 'data': '192.168.1.2'}),
            ('n5', {'type': 'EMAILADDR', 'data': 'bad@evil.com'}),
            ('n6', {'type': 'DOMAIN_NAME', 'data': 'evil3.com'}),
            ('n7', {'type': 'IP_ADDRESS', 'data': '10.0.0.1'}),
        ]
        
        for node_id, attrs in nodes:
            G.add_node(node_id, **attrs)
        
        # Add edges (simulate relationships)
        edges = [
            ('n2', 'n1'), ('n3', 'n1'),  # Two domains point to same IP
            ('n6', 'n4'),
            ('n5', 'n2'), ('n5', 'n3'),  # Email connected to domains
            ('n2', 'n6'),  # Domain connections
        ]
        
        for src, tgt in edges:
            G.add_edge(src, tgt, type='RELATED')
        
        print(f"Created test graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Initialize analyzer
        analyzer = GraphAnalyzer(G)
        print("✓ GraphAnalyzer initialized")
        
        # Test community detection
        communities = analyzer.detect_communities_louvain()
        print(f"✓ Louvain community detection:")
        print(f"  - Found {communities['num_communities']} communities")
        print(f"  - Modularity score: {communities['modularity']:.4f}")
        
        # Test label propagation
        lp_communities = analyzer.detect_communities_label_propagation()
        print(f"✓ Label propagation:")
        print(f"  - Found {lp_communities['num_communities']} communities")
        
        # Test anomaly detection
        anomalies = analyzer.detect_anomalies(z_score_threshold=1.5)
        print(f"✓ Anomaly detection:")
        print(f"  - Isolated nodes: {len(anomalies['isolated_nodes'])}")
        print(f"  - Bridge nodes: {len(anomalies['bridge_nodes'])}")
        print(f"  - Degree outliers: {len(anomalies['degree_outliers'])}")
        
        # Test centrality measures
        pagerank = analyzer.calculate_centrality('pagerank')
        print(f"✓ PageRank centrality calculated")
        print(f"  - Top node: {max(pagerank, key=pagerank.get)} (score: {max(pagerank.values()):.4f})")
        
        betweenness = analyzer.calculate_centrality('betweenness')
        print(f"✓ Betweenness centrality calculated")
        
        # Test infrastructure overlap
        overlaps = analyzer.detect_infrastructure_overlap()
        print(f"✓ Infrastructure overlap detection:")
        print(f"  - Found {len(overlaps)} shared infrastructure nodes")
        
        print("\n✅ Graph Algorithms Test: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Graph Algorithms Test: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """Test database integration"""
    print("\n" + "="*60)
    print("TEST 3: Database Integration")
    print("="*60)
    
    try:
        from spiderfoot.db import SpiderFootDb
        import json
        
        # Create test database
        opts = {'__database': '/tmp/test_prism_db.db'}
        dbh = SpiderFootDb(opts, init=True)
        print("✓ Database initialized")
        
        # Create test scan
        scan_id = 'test_scan_db_456'
        dbh.scanInstanceCreate(scan_id, 'DB Test Scan', 'test.com')
        print("✓ Test scan created")
        
        # Test storing graph correlation
        success = dbh.storeGraphCorrelation(
            scanId=scan_id,
            correlation_type='community',
            algorithm='louvain',
            entities=json.dumps(['entity1', 'entity2', 'entity3']),
            metadata=json.dumps({'modularity': 0.75, 'size': 3}),
            score=0.85
        )
        print(f"✓ Graph correlation stored: {success}")
        
        # Test retrieving correlations
        correlations = dbh.getGraphCorrelations(scan_id)
        print(f"✓ Graph correlations retrieved: {len(correlations)} found")
        
        if correlations:
            corr = correlations[0]
            print(f"  - Type: {corr[2]}")
            print(f"  - Algorithm: {corr[3]}")
            print(f"  - Score: {corr[6]}")
        
        # Cleanup
        os.remove('/tmp/test_prism_db.db')
        
        print("\n✅ Database Integration Test: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Database Integration Test: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_correlation_engine():
    """Test full correlation engine"""
    print("\n" + "="*60)
    print("TEST 4: Full Correlation Engine")
    print("="*60)
    
    try:
        from spiderfoot.graph_engine import SpiderFootGraphEngine
        from spiderfoot.graph_algorithms import GraphAnalyzer
        from spiderfoot.graph_correlation import GraphCorrelator
        from spiderfoot.db import SpiderFootDb
        import networkx as nx
        
        # Setup
        opts = {'__database': '/tmp/test_correlation.db'}
        dbh = SpiderFootDb(opts, init=True)
        scan_id = 'test_corr_789'
        dbh.scanInstanceCreate(scan_id, 'Correlation Test', 'target.com')
        
        # Create engine and build test graph
        engine = SpiderFootGraphEngine(dbh, scan_id)
        
        # Add test entities
        for i in range(10):
            engine.add_entity_node(
                f'node{i}',
                'IP_ADDRESS' if i % 2 == 0 else 'DOMAIN_NAME',
                f'test{i}.com' if i % 2 == 1 else f'10.0.0.{i}',
                {'test': True}
            )
        
        # Add test edges
        for i in range(9):
            engine.add_relationship_edge(f'node{i}', f'node{i+1}', 'RELATED')
        
        print(f"✓ Test graph built: {engine.graph.number_of_nodes()} nodes, {engine.graph.number_of_edges()} edges")
        
        # Create analyzer
        analyzer = GraphAnalyzer(engine.graph)
        print("✓ Analyzer created")
        
        # Create correlator
        correlator = GraphCorrelator(engine, analyzer)
        print("✓ Correlator created")
        
        # Run all correlations
        correlations = correlator.run_all_correlations()
        print(f"✓ Correlations generated: {len(correlations)} found")
        
        # Display results
        for corr in correlations[:3]:  # Show first 3
            print(f"  - {corr['correlation_type']}: {corr['title']}")
        
        # Cleanup
        os.remove('/tmp/test_correlation.db')
        
        print("\n✅ Correlation Engine Test: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Correlation Engine Test: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PRISM GRAPH CORRELATION ENGINE - TEST SUITE")
    print("="*60)
    
    results = []
    
    results.append(('Graph Engine', test_graph_engine()))
    results.append(('Graph Algorithms', test_graph_algorithms()))
    results.append(('Database Integration', test_database_integration()))
    results.append(('Correlation Engine', test_correlation_engine()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Graph correlation engine is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
