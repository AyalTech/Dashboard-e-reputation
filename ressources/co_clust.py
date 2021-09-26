from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from coclust.coclustering import CoclustMod


def transform_doc_term_matrix(df_unique_text_clean, n_top_terms):
    df_sentences = pd.DataFrame(data=df_unique_text_clean['text_clean'].tolist(), columns=['sentences'])
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df_sentences['sentences'].values.astype(str))

    matrice_term_doc = pd.DataFrame(data=X.toarray(), columns=vectorizer.get_feature_names())
    matrice_term_doc.insert(0, 'id_tweet', df_unique_text_clean['id_tweet'])
    matrice_term_doc = matrice_term_doc.dropna()
    matrice_term_doc = matrice_term_doc.drop(columns=['id_tweet'])

    df_id_idTweets = pd.DataFrame(matrice_term_doc, columns=['id_tweet'])
    df_id_idTweets.index.name = 'id'

    matrice_term_doc_count = pd.DataFrame(matrice_term_doc.sum(axis=0), columns=['counts_by_word'])
    matrice_term_doc_count = matrice_term_doc_count.sort_values(by='counts_by_word', ascending=False)

    matrice_term_doc_count = matrice_term_doc_count.iloc[:n_top_terms]
    matrice_term_doc_top10 = matrice_term_doc[matrice_term_doc_count.index]

    return matrice_term_doc_top10


def plot_cluster_top_terms_V2(in_data, all_terms, nb_top_terms, model):
    x_label = "number of occurences"
    plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(hspace=0.200)
    plt.suptitle("      Top %d terms" % nb_top_terms, size=15)
    number_of_subplots = model.n_clusters

    for i, v in enumerate(range(number_of_subplots)):
        # Get the row/col indices corresponding to the given cluster
        row_indices, col_indices = model.get_indices(v)
        # Get the submatrix corresponding to the given cluster
        cluster = model.get_submatrix(in_data, v)
        # Count the number of each term
        p = cluster.sum(0)
        p = np.asmatrix(p)
        print(p.shape, type(p))
        t = p.getA().flatten()
        #t = p
        # Obtain all term names for the given cluster
        tmp_terms = np.array(all_terms)[col_indices]
        # Get the first n terms
        max_indices = t.argsort()[::-1][:nb_top_terms]

        pos = np.arange(nb_top_terms)

        v = v + 1
        ax1 = plt.subplot(number_of_subplots, 1, v)
        ax1.barh(pos, t[max_indices][::-1])
        ax1.set_title("Cluster %d (%d terms)" % (v, len(col_indices)), size=11)

        plt.yticks(.4 + pos, tmp_terms[max_indices][::-1], size=9.5)
        plt.xlabel(x_label, size=9)
        plt.margins(y=0.05)
        #_remove_ticks()
        plt.tick_params(axis='both', which='both', bottom='True', top='False',
                        right='False', left='False')

    # Tight layout often produces nice results
    # but requires the title to be spaced accordingly
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.savefig('data/coclust.jpg')
    plt.clf()


def run_coclust(matrice_term_doc):
    bestmodel = CoclustMod(n_clusters=2, random_state=0)
    bestmodel.fit(matrice_term_doc.values)

    for i in range(3, 6):
        tmp = CoclustMod(n_clusters=i, random_state=0)
        tmp.fit(matrice_term_doc.values)
        if tmp.modularity > bestmodel.modularity:
            bestmodel = tmp

    terms = [x for x in matrice_term_doc.columns]
    plot_cluster_top_terms_V2(in_data=matrice_term_doc.values, all_terms=terms, nb_top_terms=5, model=bestmodel)

    n_clust = 1

    # Extract a co-cluster matrix data_c
    row_indices, col_indices = bestmodel.get_indices(n_clust)
    data_c = bestmodel.get_submatrix(matrice_term_doc.values, n_clust)

    # Count the number of each term within the co-cluster matrix
    t = data_c.sum(axis=0)

    # Obtain all term names for the co-cluster matrix
    tmp_terms = [terms[i] for i in col_indices]
    return data_c, tmp_terms, t

