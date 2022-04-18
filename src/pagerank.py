import networkx as nx
import operator
import random

import yaml

import utility.io as io


def pageranks_walk(G, numIter):
    visits = {}
    for v in G.nodes():
        visits[v] = 0
	
    v = random.choice(list(G.nodes()))

    for i in range(0, numIter):
        if i % 10000 == 0:
            print(i)
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


if __name__ == "__main__":
    """
    Read in graph data produced and run pagerank algorithm
    """
    config = yaml.safe_load(open('config.yml'))

    graph_filename = io.get_graph_filename(config)
    
    G = nx.read_weighted_edgelist(graph_filename, create_using=nx.DiGraph())

    if config['weight_time_difference']:
        D = nx.MultiDiGraph()

        for e in G.edges():
            E = G.get_edge_data(e[0],e[1])

            D.add_edge(e[0], e[1])

            for i in range(int(E['weight'])):
                D.add_edge(e[0], e[1])
        
        G = D

    p = pageranks_walk(G, 1000000)
    p = sorted(p.items(), key=operator.itemgetter(1), reverse=True)

    for i, (runner, score) in enumerate(p[0:50]):
        print(f"{i + 1}: {runner}")

