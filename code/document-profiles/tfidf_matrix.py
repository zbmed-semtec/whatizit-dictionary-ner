import os
import time
import argparse
import re
from tqdm import tqdm
import pandas as pd
import numpy as np
import logging
import xml.etree.ElementTree as ET
from scipy import spatial
from typing import List, Dict, Tuple, Set


if not os.path.exists("./logging"):
    os.makedirs("./logging")

logging.basicConfig(filename='./logging/relish_tfidf_matrix.log', filemode='a', level=logging.DEBUG)


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
                         
                         
def whatizit_annotation_extractor(annotations_path: str, namespace: dict) -> Tuple[Dict, List, Set]:
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
    pmids : list
        PMIDS of all XML files.
    prevalant_mesh_ids : set
        Set containing all mesh ids that exist as part of the RELISH Corpus.
    """
    annotations = {}
    pmids = []
    prevalant_mesh_ids = set()
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
                prevalant_mesh_ids.add(mesh_id)
                if mesh_id not in annotations[pmid]:
                    annotations[pmid][mesh_id] = {}
                    annotations[pmid][mesh_id]["Term"] = tagged.text
                    annotations[pmid][mesh_id]["Freq_term_in_doc"] = 1
                else:
                    annotations[pmid][mesh_id]["Freq_term_in_doc"] += 1

    return annotations, pmids, prevalant_mesh_ids


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


def get_idf(len_corpus:int) -> list:
    """
    Calculates the Inverse Document Frequency across all the prevalant mesh ids.
    Parameters
    ----------
    len_corpus : int
        Length of the RELISH corpus.

    Returns
    -------
    idfs : list
        List of idf values for all mesh ids.    
    """
    idfs = []
    for mesh_id_index in range(len(prevalant_mesh_ids)):
        df_value = dfs[mesh_id_index]
        idf_value = np.log(len_corpus/df_value)
        idfs.append(idf_value)
    return idfs

def get_tf_idf_vectorized(pmid_index: int, mesh_id_indices: np.array) -> np.ndarray:
    """
    Parameters
    ----------
    pmid_index : int
        Index of the PMID for which the tf-idf values are to be computed.
    mesh_id_indices : np.array
        Numpy array consisting of total number of mesh terms.

    Returns
    -------
    tf_idf_values : np.array
        Numpy array consisting of tf-idf values for all mesh terms for the input pmid.
    """
    tf_values = tf_matrix[pmid_index, mesh_id_indices]
    idf_values = np.array(idfs)[mesh_id_indices]
    tf_idf_values = tf_values * idf_values
    return tf_idf_values


def get_tf_idf_vectorized(pmid_index: int, mesh_id_indices: list, len_corpus: int) -> np.ndarray:
    tf_values = tf_matrix[pmid_index, mesh_id_indices]
    df_values = dfs[mesh_id_indices]
    idf_values = np.log(len_corpus / df_values)
    tf_idf_values = tf_values * idf_values
    return tf_idf_values


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

    mesh_id_indices = np.arange(len(mesh_ids))

    for pmid_index, pmid in enumerate(pmids):
        # Refresh from memory
        if tracking_counter == chunk_size:
            # Track the no. of iterations performed and the time taken
            time_taken = time.time() - start_time
            logging.info(f"{pmid_index} iterations completed in {time_taken} seconds\n")

            tracking_counter = 0

        tf_idf_empty_matrix[pmid_index, :] = get_tf_idf_vectorized(pmid_index, mesh_id_indices, len_corpus)

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



def get_cosine_similarity(input_file: str, pmids: list, tfidf_matrix: np.memmap, output_matrix_name: str) -> None:
    """
    Creates a 4 column matrix by appending cosine similarity scores for all existing pairs
    of PMIDs to the Relevance matrix.
    Parameters
    ----------
    input_file : str
        File path for relevance matrix.
    pmids : list
        List of all PMIDs.
    tfidf_matrix : np.memmap
        Numpy memory map of TF-IDF matrix.
    output_matrix_name : str
        File path for generated cosine similarity matrix.
    """
    matrix_df = pd.read_csv(input_file, sep='\t', low_memory= False)

    tf_idf_dict = {pmid : tfidf_matrix[index] for index, pmid in enumerate(pmids)}
    pmid_pairs = list(zip(matrix_df["PMID1"], matrix_df["PMID2"]))

    cosine_similarities = []

    for ref_pmid, assessed_pmid in tqdm(pmid_pairs, total=len(pmid_pairs), desc="Calculating Cosine Similarities"):
        cosine_similarity = None
        try:
            ref_pmid_vector = tf_idf_dict.get(str(ref_pmid))
            assessed_pmid_vector = tf_idf_dict.get(str(assessed_pmid))

            if ref_pmid_vector is not None and assessed_pmid_vector is not None:
                cosine_similarity = round(1 - spatial.distance.cosine(ref_pmid_vector, assessed_pmid_vector), 2)
        except:
            cosine_similarity = ""
        cosine_similarities.append(cosine_similarity)
    
    matrix_df['Cosine Similarity'] = cosine_similarities

    matrix_df.to_csv(output_matrix_name, index=False, sep="\t", columns=['PMID1', 'PMID2', 'Relevance', 'Cosine Similarity'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--annotations_path", type=str, help="Path for annotated XML files")
    parser.add_argument("-d", "--mesh_dict_file", type=str, help="Path for MESH MWT dictionary")
    parser.add_argument("-r", "--relevance_matrix", type=str, help="Path for relevance matrix")
    parser.add_argument("-m", "--matrix_name", type=str, help="Path for output cosine similarity matrix")
    args = parser.parse_args()

    namespace = {"z": "https://github.com/zbmed-semtec/whatizit-dictionary-ner#"}
    annotations, pmids, prevalant_mesh_ids = whatizit_annotation_extractor(args.annotations_path, namespace)
    logging.info('Extracted annotations and prevalant mesh terms.')

    tf_empty_matrix = create_matrix("tf_matrix", prevalant_mesh_ids, pmids)
    fill_tf_matrix(5000, tf_empty_matrix, pmids, prevalant_mesh_ids, annotations)
    tf_matrix = load_numpy_matrix(pmids, prevalant_mesh_ids, "tf_matrix")
    logging.info('Created TF matrix.')

    dfs = get_df(tf_matrix)
    logging.info('Calculated document frequencies.')
    
    idfs = get_idf(len(pmids))
    logging.info('Calculated inverse document frequencies.')

    tf_idf_empty_matrix = create_matrix("tf_idf_matrix", prevalant_mesh_ids, pmids)
    fill_tf_idf_matrix(5000, tf_idf_empty_matrix, pmids, prevalant_mesh_ids, len(pmids))
    tf_idf_matrix = load_numpy_matrix(pmids, prevalant_mesh_ids, "tf_idf_matrix")
    logging.info('Created TF-IDF matrix.')

    get_cosine_similarity(args.relevance_matrix, pmids, tf_idf_matrix, args.matrix_name)
    logging.info('Calculated cosine similarity scores.')