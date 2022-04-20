import math
import random
import networkx as nx
import yaml

import utility.io as io


"""
Connor Wooding
Graph Mining
CSCI 4964
Homework 1
"""


def bow_tie(D):
    """
    """
    # (a) Number of weakly connected components.
    num_weak_comps = nx.number_weakly_connected_components(D)

    print("  Num weak comps:", num_weak_comps)

    # (b) Number of strongly connected components.
    num_strong_comps = nx.number_strongly_connected_components(D)

    print("  Num strong comps:", num_strong_comps)

    # (c) Number of trivial strongly connected components.
    num_trivial_strong_comps = 0
    scc = list(nx.strongly_connected_components(D))
    for c in scc:
        if len(c) == 1:
            num_trivial_strong_comps += 1

    print("  Num trivial strong comps:", num_trivial_strong_comps)

    # (d) Number of vertices in each of SCC, IN, and OUT.
    scc = list(nx.strongly_connected_components(D))
    SCC = set(max(scc, key=len))

    v = next(iter(SCC))
    IN = set(nx.bfs_tree(D, v, reverse=True).nodes()) - SCC
    OUT = set(nx.bfs_tree(D, v).nodes()) - SCC

    num_in_SCC = len(SCC)
    num_in_IN = len(IN)
    num_in_OUT = len(OUT)

    print("  Num in SCC:", num_in_SCC)
    print("  Num in IN:", num_in_IN)
    print("  Num in OUT:", num_in_OUT)

    # (e) Number of vertices in each of Tendrils and Tubes.
    num_in_tendrils = 0
    num_in_tubes = 0
    num_tendrils = 0
    num_tubes = 0

    # Largest WCC will contain SCC, IN, OUT, Tubes, and Tendrils
    wcc = nx.weakly_connected_components(D)
    WCC = max(wcc, key=len)

    # Get subgrah with only Tubes and Tendrils
    TT = D.subgraph(WCC).copy()
    TT.remove_nodes_from(SCC)
    TT.remove_nodes_from(IN)
    TT.remove_nodes_from(OUT)

    # For each wcc in Tubes and Tendrils subgraph, determine which it is and add to counts
    for tt in nx.weakly_connected_components(TT):
        is_tube = False
        for v in tt:
            v_to_out = len(OUT.intersection(nx.bfs_tree(D, v).nodes())) > 0
            v_from_in = len(IN.intersection(nx.bfs_tree(D, v, reverse=True).nodes())) > 0
            if v_to_out and v_from_in:
                is_tube = True

        if is_tube:
            num_tubes += 1
            num_in_tubes += len(tt)
        else:
            # Must be a Tendril
            num_tendrils += 1
            num_in_tendrils += len(tt)

    print("  Num in tendrils:", num_in_tendrils)
    print("  Num in tubes:", num_in_tubes)

    # (f) Number Tendrils and number of Tubes.

    print("  Num tendrils:", num_tendrils)
    print("  Num tubes:", num_tubes)


def degree_stats(degrees):
    """
    Get min, max, and avg of the degrees given
    """
    d_min = float('inf')
    d_max = 0
    d_sum = 0
    for _, d in degrees:
        d_sum += d
        if d > d_max:
            d_max = d
        if d < d_min:
            d_min = d
    
    d_avg = d_sum / len(degrees)

    return d_min, d_max, d_avg


if __name__ == "__main__":
    """
    Print bow tie structure and degree stats for given graph
    """
    config = yaml.safe_load(open('config.yml'))

    graph_filename = io.get_graph_filename(config)
    D = nx.read_weighted_edgelist(graph_filename, create_using=nx.DiGraph())
    
    print("Bow Tie Structure for Meet Results:")
    bow_tie(D)
    
    d_min, d_max, d_avg = degree_stats(D.in_degree())
    print(f"In Degree:\n  Min: {d_min}\n  Max: {d_max} \n  Avg {d_avg:.3f}")

    d_min, d_max, d_avg = degree_stats(D.out_degree())
    print(f"Out Degree:\n  Min: {d_min}\n  Max: {d_max} \n  Avg {d_avg:.3f}")