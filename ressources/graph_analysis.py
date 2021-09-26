import numpy as np
from sklearn.preprocessing import normalize
import igraph
import random


def random_color():
    colors = ['purple', 'cyan', 'green', 'red', 'magenta', 'yellow']
    return random.choice(colors)


def createGraphByCluster(n_clust, n_top, critereSimilarity, color):
    # Extract a co-cluster matrix data_c
    row_indices, col_indices = bestmodel.get_indices(n_clust)
    data_c = bestmodel.get_submatrix(matrice_term_doc.values, n_clust)

    # Count the number of each term within the co-cluster matrix
    t = data_c.sum(axis=0)

    # Obtain all term names for the co-cluster matrix
    tmp_terms = [terms[i] for i in col_indices]
    # print(tmp_terms)

    # Get the first n terms sorted by deacreasing frequency within the co-cluster
    max_indices = (-t).argsort()  # argsort is by increasing
    max_indices = max_indices.tolist()[:n_top]
    # print(max_indices)
    top_terms = [tmp_terms[i] for i in max_indices]

    freq = [0] * n_top
    for i in range(n_top):
        freq[i] = t.tolist()[max_indices[i]]

    # Normalize the column vectors to b of L2 unit length
    # print(max_indices)
    data_c_top = data_c[:, max_indices]
    data_c_top_norm = normalize(data_c_top, axis=0, norm='l2')

    # Compute the similarity (ie., weighted adjacency matrix)
    S_c = data_c_top_norm.T @ data_c_top_norm
    # Make a graph from the adjacency matrix
    g = igraph.Graph.Weighted_Adjacency((S_c > critereSimilarity).tolist(), mode="undirected")

    # Set words as vertices label
    g.vs["name"] = top_terms
    g.vs["label"] = g.vs["name"]
    g.vs["color"] = color

    # Set size as vertices size by frequence of term in documents
    size_vertex = [0] * n_top
    for i in range(n_top):
        size_vertex[i] = t.tolist()[max_indices[i]]
        # print(size_vertex[i])
    size_vertex_norm = norm = [float(i) / (sum(size_vertex) - size_vertex[0]) * 400 for i in size_vertex]

    g.vs["size"] = size_vertex_norm

    # Set cosine similarity as edge width
    edge_w = [0] * len(g.get_edgelist())
    for ie, (i, j) in enumerate(g.get_edgelist()):
        if i == j:
            edge_w[ie] = 0
        else:
            edge_w[ie] = -np.log(S_c[i, j]) * 2

    edge_w_color = [""] * len(g.get_edgelist())

    for ie, edge_value in enumerate(edge_w):
        if edge_value > 2.4:
            edge_w_color[ie] = "#126600"
        elif 2.35 < edge_value < 2.4:
            edge_w_color[ie] = "#25cc00"
        else:
            edge_w_color[ie] = "#2eff00"

    g.es["weight"] = edge_w
    g.es["width"] = g.es["weight"]
    g.es["color"] = edge_w_color

    igraph.plot(g, "data/graph.png", margin=50, bbox=(500, 900))
    g.write_lgl('data/graph.txt')
    listOut = list()
    for i in range(0, bestmodel.n_clusters):
        g = createGraphByCluster(i, 10, 0.2, random_color())
        listOut.append(g);
    return g
