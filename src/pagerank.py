import math
import networkx as nx
import operator
import random
import yaml

from scraper import get_championship_results
import utility.io as io


def pageranks_walk(G, numIter):
    """
    Random walk from node to node numIter times
    """
    visits = {}
    for v in G.nodes():
        visits[v] = 0
	
    v = random.choice(list(G.nodes()))
    for i in range(0, numIter):
        visits[v] += 1
		
        if G.out_degree(v) > 0:
            v = random.choice(list(G.successors(v)))
        else:
            v = random.choice(list(G.nodes()))
	
    pageranks = {}
    for v in G.nodes():
        pageranks[v] = visits[v] / numIter
	
    return pageranks


def pageranks_calc(G, numIter):
    """
    Explicitly calculate PageRanks in a vertex-centric iterative way
    """
    pageranks = {}
    sinks = 0
    sinksNext = 0
    for v in G.nodes():
        pageranks[v] = 1.0 / G.order()
        if G.out_degree(v) == 0:
            sinks += pageranks[v]
            
    for i in range(0, numIter):
        for v in G.nodes():
            pageranks[v] = sinks / G.order()
		
            for e in G.in_edges(v):
                u = e[0]
                pageranks[v] += pageranks[u] / G.out_degree(u)
				
            if G.out_degree(v) == 0:
                sinksNext += pageranks[v]
                
        sinks = sinksNext
        sinksNext = 0
    
    return pageranks


def pageranks_custom(G, numIter):
    """
    Custom pagerank that does a random walk for numIter at every vertex
    """
    visits = {}
    for v in G.nodes():
        visits[v] = 0

    nodes = list(G.nodes())
    for v in nodes:
        for i in range(0, numIter):
            visits[v] += 1
            
            if G.out_degree(v) > 0:
                v = random.choice(list(G.successors(v)))
            else:
                v = random.choice(list(G.nodes()))
	
    pageranks = {}
    for v in G.nodes():
        pageranks[v] = visits[v] / (numIter * len(nodes))
    
    return pageranks


def calculate_statistics(method, predicted_result, actual_result):
    """
    Calculate the two different statistics on the predicted results
    """
    # Sort in order to get prediction
    predicted_result = sorted(predicted_result.items(), key=operator.itemgetter(1), reverse=True)

    # Filter to only include runners that were in the race
    predicted_result = [p[0] for p in predicted_result if p[0] in actual_result]
    actual_result = [runner for runner in actual_result]

    for i, p in enumerate(predicted_result[0:10]):
        print(i + 1, p)

    # Root Mean Square and Average Distance Off
    rms = 0
    ad = 0
    for i, runner in enumerate(predicted_result):
        j = actual_result.index(runner)
        
        rms += (i - j)**2
        ad += abs(i - j)

    rms /= len(predicted_result)
    rms = math.sqrt(rms)
    ad /= len(predicted_result)

    # All American Percent Correct(Top 40)
    aa = 0
    predicted_aa = predicted_result[0:40]
    actual_aa = actual_result[0:40]
    for runner in predicted_aa:
        if runner in actual_aa:
            aa += 1

    aa = 100 * aa / 40

    print(f"{method}:")
    print(f"  RMS Of Prediction: {rms:.1f}")
    print(f"  Average Absolute Difference: {ad:.1f}")
    print(f"  Percent All Americans Correct: {aa:.1f}")


if __name__ == "__main__":
    """
    Read in graph data produced and run pagerank algorithm
    """
    config = yaml.safe_load(open('config.yml'))
    for d in ("d3", "d2", "d1"):
        config['file']['division_dir'] = d
        print(config['file']['division_dir'])

        # Get actual results
        championship_filename = io.get_championship_filename(config)
        individual_result, team_result = get_championship_results(championship_filename)

        graph_filename = io.get_graph_filename(config)
        G = nx.read_weighted_edgelist(graph_filename, create_using=nx.DiGraph())

        if config['only_nationals_runners']:
            for v in dict(G.nodes()):
                if v not in individual_result:
                    G.remove_node(v)

        D = nx.MultiDiGraph()
        for e in G.edges():
            E = G.get_edge_data(e[0],e[1])
            D.add_edge(e[0], e[1])
            
            if config['weight_time_difference']:
                for i in range(int(E['weight'])):
                    D.add_edge(e[0], e[1])
        
        # Get actual results
        championship_filename = io.get_championship_filename(config)
        individual_result, team_result = get_championship_results(championship_filename)

        # Run each type of pagerank
        pagerank = pageranks_walk(D, 100000)
        calculate_statistics("Random Walk", pagerank, individual_result)

        pagerank = pageranks_calc(D, 10)
        calculate_statistics("Calculated", pagerank, individual_result)

        pagerank = pageranks_custom(D, 10000)
        calculate_statistics("Custom", pagerank, individual_result)