from calendar import c
from os import remove
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import numpy as np
import yaml
import networkx as nx
import nxviz as nv

import utility.io as io
from utility.helpers import get_child_string, get_table_name

def remove_men(s):
    """
    Remove "(Men)" from the end of a string
    """
    parentheses = s.index("(")
    return s[0: parentheses - 1]


def write_results_to_file(events, cluster_values):
    """
    Write events and cluster values results to a file
    """
    f = open("out.csv", "w")
    for e in events:
        f.write(e)
        f.write(",")

    f.write("\n")

    for v in cluster_values:
        f.write(str(v))
        f.write(",")

    f.close()


if __name__ == "__main__":
    """
    Analyze Top 100 TFRRS Pages.  Creates Relational Graphs
    """
    config = yaml.safe_load(open('config.yml'))

    track_list_filename = io.get_track_list_filename(config)
    track_list_page = open(track_list_filename, "r")
    doc = BeautifulSoup(track_list_page, "html.parser")

    edges = []
    events = []
    athletes = []
    for table in doc.find_all('table'):
        event = get_table_name(table)

        if "Men" in event and "Relay" not in event:
            event = remove_men(event)
            events.append(event)
                
            column_names = [column.string.strip() if column.string is not None else '' for column in table.find('thead').find_all('th')]
            athlete_index = column_names.index('ATHLETE')
            place_index = column_names.index('')

            for row in table.find('tbody').find_all('tr'):
                row = row.find_all('td')
                athlete = get_child_string(row[athlete_index])
                place = get_child_string(row[place_index])
                edges.append((event, athlete))
                if athlete not in athletes:
                    athletes.append(athlete)

    # Create Bipartite Graph
    B = nx.Graph()
    B.add_nodes_from(events, bipartite=0)
    B.add_nodes_from(athletes, bipartite=1)
    B.add_edges_from(edges)

    print(f"Event Graph has {len(events)} events")
    print(f"Event Graph has {len(athletes)} athletes")
    print(f"{nx.number_connected_components(B)} Connected Components")

    # Create Degree Histogram
    degree_sequence = sorted((d for n, d in B.degree() if n not in events), reverse=True)
    plt.bar(*np.unique(degree_sequence, return_counts=True))
    plt.title("Degree histogram")
    plt.xlabel("Degree")
    plt.ylabel("# of Nodes")
    plt.show()
    
    # Display Degree Graph with circos
    for n, d in B.nodes(data=True):
        B.nodes[n]["degree"] = B.degree(n)

    fig, ax = plt.subplots(figsize=(7, 7))
    nv.circos(B, sort_by="degree", group_by="bipartite", node_color_by="bipartite", node_enc_kwargs={"size_scale": 5})
    plt.show()

    # Using degree of neighbors
    cluster_values = [0] * len(events)
    for event in events:
        for athlete in B.neighbors(event):
            if B.degree(athlete) > 1:
                cluster_values[events.index(event)] += 1
    
    write_results_to_file(events, cluster_values)

    # Edge Graph of Neighbors
    E = nx.Graph()
    for e1 in events:
        for e2 in events:
            if e1 < e2:
                weight = len(list(nx.common_neighbors(B, e1, e2)))
                if weight != 0:
                    E.add_edge(e1, e2, weight=weight)
        
    # Plot Edge Graph
    pos = nx.spring_layout(E)
    labels = nx.get_edge_attributes(E, 'weight')
    nx.draw_networkx(E, pos, font_size=7, node_size=200)
    nx.draw_networkx_edge_labels(E, pos, edge_labels=labels, font_size=6)
    plt.show()

    # Print Edge Graph Weights
    edges=sorted(E.edges(data=True), key=lambda t: t[2].get('weight', 1), reverse=True)[0:5]
    for e in edges:
        print(e[0], e[1], e[2]['weight'])