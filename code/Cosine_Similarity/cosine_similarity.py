import os
import time
import logging
import pandas as pd
import numpy as np
from scipy import spatial


if not os.path.exists("../logging"):
    os.makedirs("../logging")

logging.basicConfig(filename='../logging/whatizit_similarity_matrix.log', filemode='a', level=logging.DEBUG)


def extract_pmids(input_pmid_file):
    corpus = pd.read_csv(input_pmid_file, sep='\t', dtype=str)
    return sorted(list(corpus['PMID']))


def create_matrix(matrix_name, pmids):
    similarity_matrix = np.memmap(matrix_name, dtype='float32', mode='w+', shape=(len(pmids), len(pmids)))
    return similarity_matrix


def load_tfidf_matrix(matrix_file, len_pmids, len_mesh_ids):
    matrix = np.memmap(matrix_file, dtype='float', mode='r', shape=(len_pmids, len_mesh_ids))
    return matrix


def fill_matrix(similarity_matrix, pmids, tfidf_matrix, chunk_size, start_time):
    tracking_counter = 0

    # Matrix will be processed in memory
    matrix = np.zeros((chunk_size, len(pmids)))

    for i, ref_pmid in enumerate(pmids):

        # Refresh from memory
        if tracking_counter == chunk_size:
            # Track the no. of iterations performed and the time taken
            time_taken = time.time() - start_time
            logging.info(f"{i} iterations completed in {time_taken} seconds\n")

            index = 0
            for k in range(i - chunk_size, i):
                similarity_matrix[k] = matrix[index]
                index += 1

            tracking_counter = 0
            matrix = np.zeros((chunk_size, len(pmids)))

        for j, assessed_pmid in enumerate(pmids):
            if j < i:
                continue
            else:
                # Determine the cosine similarity score between two documents
                matrix[tracking_counter][j] = round((1 - spatial.distance.cosine(tfidf_matrix[i], tfidf_matrix[j])), 2)

        tracking_counter += 1


if __name__ == "__main__":
    start_time = time.time()
    pmids = extract_pmids("./data/RELISH_documents_2022628.tsv")
    len_pmids = len(pmids)
    len_mesh_ids = 34526
    similarity_matrix = create_matrix("./data/similarity_matrices/whatizit_cosine_similarity_matrix", pmids)
    tfidf_matrix = load_tfidf_matrix("./data/tfidf_matrices/relish/relish_tfidf_matrix", len_pmids, len_mesh_ids)
    fill_matrix(similarity_matrix, pmids, tfidf_matrix, 5000, start_time)
