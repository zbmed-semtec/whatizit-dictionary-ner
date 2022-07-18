import os
import sys
import time
import argparse
import re
import csv
import pandas as pd
import numpy as np
import logging
import xml.etree.ElementTree as ET
from scipy import spatial
from typing import List, Dict, Tuple


if not os.path.exists("../logging"):
    os.makedirs("../logging")

logging.basicConfig(filename='../logging/relish_tfidf_matrix.log', filemode='a', level=logging.DEBUG)


def extract_annotated_mesh_id(tag: ET.Element) -> str:
    """
    From a matched z:mesh tag, it extracts the correspondent MeSH ID if the
    field "id" is found.
    Parameters
    ----------
    tag : ET.Element
        Object correspondent of a <z:mesh></z:mesh> tag.
    Returns
    -------
    mesh_id: str
        Text with the mesh ID.
    """
    mesh_id_pattern = r"\/MESH\/(.*)"
    if tag.attrib.get("id"):
        mesh_id = "MESH" + \
                    re.search(mesh_id_pattern, tag.attrib.get("id")).group(1)
    else:
        mesh_id = tag.text.strip
    return mesh_id
                         
                         
def whatizit_annotation_extractor(annotations_path: str, namespace: dict) -> Tuple[Dict, List]:
    """
    Extracts annotated MeSH terms from XML files and returns the frequency of each MeSH term in each XML file.
    Parameters
    ----------
    annotations_path : str
        Filepath to all the annotated XML files.
    namespace : str
        Dictionary containing the namespace for the XML file.

    Returns
    -------
    annotations : dict
        Dictionary with keys as PMID of XML file and values as a dictionary of MeSH terms with its label and frequency.
    pmids :list
        PMIDS of all XML files.
    """
    annotations = {}
    pmids = []
    for file in sorted(os.listdir(annotations_path)):
        if file != '.DS_Store':
            filename = os.path.join(annotations_path, file)
            root = ET.parse(filename).getroot()
            pmid = root[0].find("id").text.strip()
            pmids.append(pmid)
            annotations[pmid] = {}
            total_terms_in_doc = len(root.findall("document/passage/text/z:mesh", namespace))
            annotations[pmid]["Total_terms"] = total_terms_in_doc
            for tagged in root.findall("document/passage/text/z:mesh", namespace):
                mesh_id = extract_annotated_mesh_id(tagged)
                if mesh_id not in annotations[pmid]:
                    annotations[pmid][mesh_id] = {}
                    annotations[pmid][mesh_id]["Term"] = tagged.text
                    annotations[pmid][mesh_id]["Freq_term_in_doc"] = 1
                else:
                    annotations[pmid][mesh_id]["Freq_term_in_doc"] += 1

    return annotations, pmids


def get_mesh_ids(mesh_filepath: str) -> List:
    """
    Extracts all MeSH Class IDs from the MeSH CSV file.
    Parameters
    ----------
    mesh_filepath : str
        Filepath to the MeSH CSV file.

    Returns
    -------
    mesh_ids : list
        All MeSH IDs.
    """
    mesh_ids = []
    csv.field_size_limit(sys.maxsize)
    data = pd.read_csv(mesh_filepath, engine='python')
    for i in range(len(data)):
        if data['Class ID'].iloc[i].startswith('http://purl.bioontology.org/ontology/MESH/'):
            mesh_id = ((data['Class ID'].iloc[i]).split('ontology/')[1]).replace('/', '')
            mesh_ids.append(mesh_id)
    return mesh_ids


def get_prevalant_mesh_ids(pmids: list, mesh_ids: list, annotations: dict) -> list:
    """
    Extracts only those mesh terms that are present in the given corpus.
    Parameters
    ----------
    pmids : list
        PMIDS of all XML files.
    mesh_ids : list
        All MeSH IDs.
    annotations : dict
        Dictionary of PMIDs with its corresponding mesh terms and the frequency.
    Returns
    -------
    relevant_mesh_ids : list
        List of all MeSH terms that are present in the corpus.
    """
    prevalant_mesh_ids = []
    for pmid in pmids:
        for mesh_id in mesh_ids:
            if mesh_id in annotations[pmid] and mesh_id not in prevalant_mesh_ids:
                prevalant_mesh_ids.append(mesh_id)
    return prevalant_mesh_ids


def create_matrix(matrix_name: str, mesh_ids: list, pmids: list) -> np.memmap:
    """
    Creates an empty numpy memory-map of the required dimensions based on the mesh_ids and pmids.
    Parameters
    ----------
    matrix_name : str
        Name of the matrix.
    mesh_ids : list
        All prevalent MeSH IDs.
    pmids : list
        PMIDS of all XML files.

    Returns
    -------
    matrix : np.memmap
        Empty numpy memory map with rows as PMIDs and each column as one MeSH Term.
    """
    matrix = np.memmap(matrix_name, dtype='float', mode='w+', shape=(len(pmids), len(mesh_ids)))
    return matrix


def get_tf(pmid: int, mesh_id: int, annotations: dict) -> float:
    """
    Calculates the term frequency value for the MesH term in the pmid article.
    Parameters
    ----------
    pmid : int
        Article for which tf value is to be calculated.
    mesh_id : int
        MeSH term for which tf value is to be calculated.
    annotations : dict
        Dictionary of annotated MeSH terms.
    Returns
    -------
    tf : float
        Term frequency value.
    """
    frequency = annotations[pmid][mesh_id]["Freq_term_in_doc"]
    total_terms = annotations[pmid]["Total_terms"]
    tf = round(frequency/total_terms, 5)
    return tf


def fill_tf_matrix(chunk_size: int, tf_empty_matrix: np.memmap, pmids: list, mesh_ids: list, annotations: dict) -> np.memmap:
    """
    Calculates and creates the TF value matrix for all the MeSH terms for the given corpus.
    Parameters
    ----------
    chunk_size : int
        Chunk size per iteration.
    tf_empty_matrix : np.memmap
        Empty tf matrix.
    pmids : list
        PMIDS of all XML files.
    mesh_ids : list
        All MeSH IDs.
    annotations : dict
        Dictionary of all annotated MeSH terms with corresponding frequency.
    Returns
    -------
    tf_matrix : np.memmap
        Numpy matrix with each cell corresponding to the term frequency value.
    """
    tracking_counter = 0
    start_time = time.time()
    logging.info("Creating tf matrix")
    for pmid_index, pmid in enumerate(pmids):
        # Refresh from memory
        if tracking_counter == chunk_size:
            # Track the no. of iterations performed and the time taken
            time_taken = time.time() - start_time
            logging.info(f"{pmid_index} iterations completed in {time_taken} seconds\n")

            tracking_counter = 0

        for mesh_id_index, mesh_id in enumerate(mesh_ids):
            if mesh_id in annotations[pmid]:
                tf_empty_matrix[pmid_index][mesh_id_index] = get_tf(pmid, mesh_id, annotations)
            else:
                continue

        tracking_counter += 1
    tf_empty_matrix.flush()
    return tf_empty_matrix


def get_df(tf_matrix: np.memmap) -> list:
    """
    Calculates the number of documents in which each MeSH term appears.
    Parameters
    ----------
    tf_matrix : np.memmap
        Term frequency matrix.

    Returns
    -------
    dfs : list
        List of document frequency for all MeSH terms.
    """
    dfs = np.count_nonzero(tf_matrix, axis=0)
    return dfs


def get_tf_idf(pmid_index: int, mesh_id_index: int, len_corpus: int) -> float:
    """
    Calculates the tf-idf values for the MeSH term in pmid article.
    Parameters
    ----------
    pmid : int
        Article for which tf-idf value is to be calculated.
    mesh_id : int
        MeSH ID for which tf-idf value is to be calculated.
    len_corpus : int
        Number of articles in the corpus.

    Returns
    -------
    tf_idf : float
        tf-idf value.
    """
    tf_value = tf_matrix[pmid_index][mesh_id_index]
    df_value = dfs[mesh_id_index]
    idf_value = np.log(len_corpus/df_value)
    tf_idf = tf_value * idf_value
    return tf_idf


def fill_tf_idf_matrix(chunk_size: int, tf_idf_empty_matrix: np.memmap, pmids: list, mesh_ids: list, len_corpus: int) -> np.memmap:
    """
    Calculates and creates the TF-IDF value matrix for all the MeSH terms for the given corpus.
    Parameters
    ----------
    chunk_size : int
        Chunk size per iteration.
    tf_idf_empty_matrix : np.memmap
        Empty tf-idf matrix.
    pmids : list
        PMIDS of all XML files.
    mesh_ids : list
        All MeSH IDs.
    len_corpus : int
        Number of documents in the given corpus.

    Returns
    -------
    tf_idf_matrix : np.memmap
        Numpy matrix with each cell corresponding to the tf-idf value.
    """
    tracking_counter = 0
    start_time = time.time()
    logging.info("Creating tf-idf matrix")
    for pmid_index, pmid in enumerate(pmids):
        # Refresh from memory
        if tracking_counter == chunk_size:
            # Track the no. of iterations performed and the time taken
            time_taken = time.time() - start_time
            logging.info(f"{pmid_index} iterations completed in {time_taken} seconds\n")

            tracking_counter = 0

        for mesh_id_index, prevalent_mesh_id_index in enumerate(mesh_ids):
            tf_idf_empty_matrix[pmid_index][mesh_id_index] = get_tf_idf(pmid_index, mesh_id_index, len_corpus)

        tracking_counter += 1

    return tf_idf_empty_matrix


def load_numpy_matrix(pmids: list, mesh_ids: list, matrix_file: str) -> np.memmap:
    """
    Loads the numpy memory map matrix.
    Parameters
    ----------
    pmids : list
        List of all PMIDs.
    mesh_ids : list
        List of all prevalent mesh ids.
    matrix_file : str
        Name of the matrix file.
    Returns
    -------
    matrix : np.memmap
        Loaded memory map matrix.
    """
    matrix = np.memmap(matrix_file, dtype='float', mode='r', shape=(len(pmids), len(mesh_ids)))
    return matrix


def get_cosine_similarity(input_file, pmids, tfidf_matrix):
    matrix_df = pd.read_csv(input_file)

    # Adds the empty 4th column to the file
    matrix_df["Cosine Similarity"] = ""

    for index, row in matrix_df.iterrows():
        ref_pmid = str(row["PMID Reference"])
        assessed_pmid = str(row["PMID Assessed"])
        try:
            # Determine the cosine similarity of the ref and assessed pmids and add to the 4th column
            ref_pmid_index = pmids.index(ref_pmid)
            assessed_pmid_index = pmids.index(assessed_pmid)
            row["Cosine Similarity"] = round((1 - spatial.distance.cosine(tfidf_matrix[ref_pmid_index], tfidf_matrix[assessed_pmid_index])), 2)

        except:
            # Leave the 4th column empty if the ref or assessed pmid not found in the dataset
            row["Cosine Similarity"] = ""

        # Make changes in the original dataframe
        matrix_df.at[index, 'Cosine Similarity'] = row['Cosine Similarity']

    matrix_df.to_csv("relish_cosine1.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotations_path", type=str, help="Path for annotated XML files")
    parser.add_argument("--mesh_file", type=str, help="Path for MESH CSV file")
    args = parser.parse_args()

    namespace = {"z": "https://github.com/zbmed-semtec/whatizit-dictionary-ner#"}
    annotations, pmids = whatizit_annotation_extractor(args.annotations_path, namespace)
    mesh_ids = get_mesh_ids(args.mesh_file)
    prevalant_mesh_ids = get_prevalant_mesh_ids(pmids, mesh_ids, annotations)
    tf_empty_matrix = create_matrix("tf_matrix", prevalant_mesh_ids, pmids)
    fill_tf_matrix(5000, tf_empty_matrix, pmids, prevalant_mesh_ids, annotations)
    tf_matrix = load_numpy_matrix(pmids, prevalant_mesh_ids, "tf_matrix")
    dfs = get_df(tf_matrix)
    tf_idf_empty_matrix = create_matrix("tf_idf_matrix", prevalant_mesh_ids, pmids)
    fill_tf_idf_matrix(5000, tf_idf_empty_matrix, pmids, prevalant_mesh_ids, len(pmids))
    tf_idf_matrix = load_numpy_matrix(pmids, prevalant_mesh_ids, "tf_idf_matrix")
    get_cosine_similarity("relish_relevance_matrix.csv", pmids, tf_idf_matrix)
