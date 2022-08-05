# Creation of TF-IDF matrices

In order to evaluate how relevant a word ([MeSH](https://www.nlm.nih.gov/mesh/meshhome.html) term) is to a document (annotated XML file) in a collection of documents (TREC and RELISH corpus), we make use of the statistical measure of TF-IDF (term frequency-inverse document frequency).

The creation of TF-IDF matrices for Whatizit annotated XML files takes as data input all the annotated XML files and a Bioportal-like CSV corresponding to a controlled vocabulary (MeSH in our case).

The entire process of annotating XML files for a required corpus (TREC and RELISH in our case) can be found [here](https://github.com/zbmed-semtec/whatizit-dictionary-ner/blob/main/docs/).

The creation of the tf-idf matrices using our [code](https://github.com/zbmed-semtec/whatizit-dictionary-ner/blob/main/code/tfidf_matrix.py) is done in two main steps: 

## Step 1 : Creation of the TF matrix.
The TF matrix accounts for how many times a MeSH term appears in each of the annotated XML file. 

We define the Term frequency as:

```
tf(t,d) = n / total annotated terms in the document
```

where,  
t : MeSH term  
d : annotated XML file  
n : frequency of MeSH term in the annotated XML file

The rows of the TF matrix correspond to the PMIDS of the XML files of the corpus(TREC/RELISH) while the columns correspond to the MeSH term.




## Step 2 : Creation of TF-IDF matrix.

The TF-IDF matrix accounts for how common or uncommon a MeSH term is amongst the TREC/RELISH corpus.

We define the Inverse Document Frequency as:

```
idf(t,D) = log (N / document frequency)
```

where,  
t : MeSH term  
D : corpus  
N : number of XML files in the corpus  
document frequency : number of documents in which each MeSH term appears

We define the Term Frequency-Inverse Document Frequency as:

```
tf-idf (t, d, D) = tf (tf, d) . idf (t, D)
```

The rows of the TF-idf matrix correspond to the PMIDS of the XML files of the corpus(TREC/RELISH) while the columns correspond to the MeSH term.  

The TF-IDF values give us an idea of how relevant a term is in our respective corpora.


|    | |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![Info](./images/information_mark.png)    | In order to account for only those MeSH terms that are present in the corpus and to avoid a document frequency of zero, we extract only the relevant MeSH terms before creating our matrices.                                                                                                                                                                                              |
|    | This implies that the number of columns in both the TF and TF-IDF matrices would only be a subset of the total MeSH vocabulary.                                                               |



----
## Executing the code

In order to run the code, please specify the following two parameters. Run the following command:

```commandline
python3 tfidf_matrix.py --annotations_path "./TREC_annotated_xmls" --mesh_file "./MESH.csv"
```

--annotations_path : File path to the Whatizit annotated XML files  
--mesh_file : File path to the Bioportal-like CSV file of the controlled vocabulary 

## Output

After the execution of the entire code, we get three particular files:  
 
+ tf_matrix  : A numpy memory-map of the tf array stored in a binary file.  
+ tf_idf_matrix : A numpy memory-map of the tf-idf array stored in a binary file.  

### Example of TF/TF-IDF matrix:

| PMID     | MESHD002477 | MESHQ000032 | MESHD002214 | .... | MESHD015533 | MESHQ000328 |
|----------|-------------|-------------|-------------|------|-------------|-------------|
| 10021334 | 0.06122     | 0.04082     | 0           |      | 0           | 0.08163     |
| 10021342 | 0           | 0.10204     | 0           |      | 0           | 0           |
| 10021362 | 0           | 0           | 0.02041     |      | 0.08163     | 0           |

Each cell corresponds to the TF value or the TF-IDF value depending on the matrix created.

----

## Code strategy

+ Used ```xml.etree``` library to parse the input annotated XML file.
+ Used ```re``` library to find all annotated ```z:mesh``` tags inside the annotated XML file and created a dictionary with each pmid as the key and the included MeSH terms with it's frequency as the value.
+ Used ```numpyp.memmap``` to create and load the TF and TF-IDF matrices.
+ Created a log file "tfidf_matrix.log" to keep track on the creation of the matrices and the number of iterations while creating the matrices.

