import math
import pandas as pd
import numpy as np
from typing import Any
from numpy import ndarray


def load_cosine_sim_matrix(cosine_similarity_matrix: str) -> pd.DataFrame:
    """
    Loads and return a pandas dataframe object of the cosine similarity matrix.
    Parameters
    ----------
    cosine_similarity_matrix : str
        Filepath for the cosine similarity matrix of existing pairs in the TSV format.
    Returns
    -------
    sim_matrix : pd.Dataframe
        Cosine similarity matrix.
    """
    sim_matrix = pd.read_csv(cosine_similarity_matrix, sep='\t')
    return sim_matrix


def get_dcg_matrix(similarity_matrix: pd.DataFrame):
    """
    Sorts the cosine similarity matrix based on the cosine similarity values (descending order) for each Reference PMID
    and creates a new TSV file based on the sorted values.
    Parameters
    ----------
    similarity_matrix : pd.Dataframe
        Cosine similarity matrix.
    """
    dcg_matrix = similarity_matrix.sort_values(['PMID Reference', 'Cosine Similarity'],
                                               ascending=[True, False], ignore_index=True)
    dcg_matrix.index = dcg_matrix.index + 1
    dcg_matrix.to_csv("./data/doc2vec-doc/dcg_doc2vec-doc.tsv", sep='\t')


def get_identity_dcg_matrix(similarity_matrix: pd.DataFrame):
    """
    Sorts the cosine similarity matrix based on the Relevance assessment scores (2's, 1's, 0's) for each Reference PMID
    and creates a new TSV file based on the sorted values.
    Parameters
    ----------
    similarity_matrix : pd.Dataframe
        Cosine similarity matrix.
    """
    idcg_matrix = similarity_matrix.sort_values(['PMID Reference', 'Relevance Assessment'],
                                                ascending=[True, False], ignore_index=True)
    idcg_matrix.index = idcg_matrix.index + 1
    idcg_matrix.to_csv("./data/doc2vec-doc/idcg_doc2vec-doc.tsv", sep='\t')


def calculate_dcg_at_n(n: int, all_assessed_pmids: pd.DataFrame) -> float:
    """
    Calculates the DCG@n value for each Reference PMID based on the input Assessed PMIDs.
    Parameters
    ----------
    n : int
        Value of n at which DCG score is to be calculated.
    all_assessed_pmids : pd.Dataframe
        Dataframe of all corresponding assessed PMIDs.
    Returns
    -------
    dcg_n : float
        DCG@n value.
    """
    dcg_n = 0
    for i, (index, row) in enumerate(all_assessed_pmids[:n].iterrows(), start=1):
        rel = row['Relevance Assessment']
        value = (2**rel - 1) / math.log2(i + 1)
        dcg_n += value
    return round(dcg_n, 4)


def calculate_idcg_at_n(n: int, sorted_assessed_pmids: pd.DataFrame) -> float:
    """
    Calculates the iDCG@n value for each Reference PMID based on the
    sorted Assessed PMIDs(based on the relevance score).
    Parameters
    ----------
    n : int
    Value of n at which iDCG score is to be calculated.
    sorted_assessed_pmids : pd.Dataframe
        Dataframe of all corresponding sorted assessed PMIDs.
    Returns
    -------
    idcg_n : float
        iDCG@n value.
    """
    idcg_n = 0
    for i, (index, row) in enumerate(sorted_assessed_pmids[:n].iterrows(), start=1):
        rel = row['Relevance Assessment']
        value = (2**rel - 1) / math.log2(i + 1)
        idcg_n += value
    return round(idcg_n, 4)


def fill_ndcg_scores(dcg_matrix: str, idcg_matrix: str) -> tuple[list[Any], ndarray]:
    """
    Creates and fills a numpy matrix based on the nDCG values for each Reference PMIDs.
    Parameters
    ----------
    dcg_matrix : str
        Filepath for TSV file of cosine similarity values sorted in the descending order.
    idcg_matrix : str
        Filepath for TSV file of cosine similarity values sorted based on relevance scores.
    Returns
    -------
    all_pmids : list
        List of all Reference PMIDs.
    ndcg_matrix : np.array
        Numpy matrix with all nDCG scores.

    """
    value_of_n = [5, 10, 15, 20, 25, 50]

    dcg_matrix = pd.read_csv(dcg_matrix, sep="\t")
    idcg_matrix = pd.read_csv(idcg_matrix, sep="\t")
    # Get list of all Reference PMIDs
    all_pmids = sorted((dcg_matrix['PMID Reference'].unique()))
    # Creates an empty numpy matrix
    ndcg_matrix = np.empty(shape=(len(all_pmids), len(value_of_n)))

    for pmid_index, pmid in enumerate(all_pmids):
        all_assessed_pmids = pd.DataFrame(dcg_matrix.loc[dcg_matrix['PMID Reference'] == pmid])
        sorted_assessed_pmids = pd.DataFrame(idcg_matrix.loc[idcg_matrix['PMID Reference'] == pmid])

        for index, n in enumerate(value_of_n):
            dcg_score = calculate_dcg_at_n(n, all_assessed_pmids)
            idcg_score = calculate_idcg_at_n(n, sorted_assessed_pmids)
            ndcg_score = round(dcg_score / idcg_score, 4)
            ndcg_matrix[pmid_index][index] = ndcg_score

    return all_pmids, ndcg_matrix


def write_to_tsv(pmids: list, ndcg_matrix: np.matrix):
    """
    Writes the nDCG matrix scores to a TSV file
    Parameters
    ----------
    pmids : list
        List of all Reference PMIDs.
    ndcg_matrix : np.array
        Numpy matrix with all nDCG scores.
    """

    ndcg_matrix = pd.DataFrame(ndcg_matrix, columns=['nDCG@5', 'nDCG@10', 'nDCG@15', 'nDCG@20', 'nDCG@25', 'nDCG@50'])
    # Insert all PMIDs
    ndcg_matrix.insert(0, 'PMIDs', pmids)
    # Calculate and append average of each nDCG score
    average_values = ['Average'] + list(ndcg_matrix[['nDCG@5', 'nDCG@10', 'nDCG@15', 'nDCG@20', 'nDCG@25', 'nDCG@50']]
                                        .mean(axis=0).round(4))
    ndcg_matrix.loc[len(ndcg_matrix.index)] = average_values
    pd.DataFrame(ndcg_matrix).to_csv("ndcg_doc2vec-doc.tsv", sep="\t")


# if __name__ == "__main__":
#     similarity_matrix = load_cosine_sim_matrix("./data/doc2vec-doc/relish_relevance_matrix_updated.tsv")
#     get_dcg_matrix(similarity_matrix)
#     get_identity_dcg_matrix(similarity_matrix)
#     fill_ndcg_scores("./data/doc2vec-doc/dcg_doc2vec-doc.tsv", "./data/doc2vec-doc/idcg_doc2vec-doc.tsv")

