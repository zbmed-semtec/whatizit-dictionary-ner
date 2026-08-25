[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15096055.svg)](https://doi.org/10.5281/zenodo.15096055) 
![Status](https://img.shields.io/badge/Status-inactive-orange)

# **whatizit-dictionary-ner**: A Dictionary-based NER Approach for TF-IDF Vector Generation using Whatizit tool

This repository contains code and documentation for a dictionary-based Named Entity Recognition (NER) approach to generate TF-IDF vectors using the [Whatizit](https://academic.oup.com/bioinformatics/article/24/2/296/227269?login=true) annotation tool. It involves preparing input XML files and annotating them using Whatizit against a controlled vocabulary, in our case, the [Medical Subject Headings](https://www.nlm.nih.gov/mesh/meshhome.html) (MeSH) ontology. 

## Table of Contents
1. [About](#about)
2. [Input Data](#input-data)
3. [Pipeline](#pipeline)
    1. [Dictionary Creation](#1-dictionary-creation)  
    2. [Preprocessing and Annotating XML Files](#2-preprocessing-and-annotating-xml-files) 
    3. [Creation of TF-IDF Vectors](#4-creation-of-tf-idf-vectors)
    4. [Calculation of Cosine Similarity](#5-calculation-of-cosine-similarity)
    5. [Evaluation](#6-evaluation)
        - [Precision@N](#precisionn)
        - [nDCG@N](#ndcgn)
4. [Getting Started](#getting-started)
5. [Documentation](#documentation)


## About
Whatizit is a text processing system that allows you to do textmining tasks on text. Whatizit was created by the Rebholz Research Group at EMBL-EBI. It is based on MONQjfa, a non-deterministic and deterministic dinite automata for Java. In our approach, we specifically make use of a [Dockerized version of Whatizit](https://github.com/zbmed-semtec/simple-whatizit-docker). 

## Input Data

##### File format: XML

The approach utilizes [XML files](https://github.com/zbmed-semtec/relish-preprocessing/tree/main/data/output/sample-files/xml) obtained from the [RELISH preprocessing pipeline](https://github.com/zbmed-semtec/relish-preprocessing/tree/main). These XMLs are structured biomedical texts resulting from initial processing, ensuring consistent formatting and content organization. While these files are not annotated with specific medical terms at this stage, they provide the groundwork for the NER process. The processes described in the following README involve using the Whatizit annotation tool for these preprocessed XMLs to identify and tag medical terms as per the MeSH vocabulary, eventually leading to the generation of TF-IDF vectors that capture the significance of these terms within the context of the biomedical texts.

## Pipeline
 The following section outlines the primary processes applied to the input XML files of the RELISH dataset in order to generate the TF-IFD vectors.

### 1. Dictionary Creation

The initial step in annotating text involves the creation of a dictionary that serves as the reference for identifying expressions within the text and associating them with concepts from a controlled vocabulary. This process starts by selecting the desired vocabulary to support. For each preferred and alternative label within the vocabulary, an entry is crafted in the dictionary.

The creation of dictionaries for Whatizit takes as data input a Biportal-like CSV or RDF file corresponding to a controlled vocabulary. We do not include the terms which are obsolete from the CSV file in our output MWT dictionary.

The generated dictionary follows a MWT format (XML-like structure) as required by Whatizit and is illustrated in the example provided below. The dictionary may include certain XML special characters (e.g., & < >), which may necessitate special handling. The XML-like format encompasses a template and individual entries, each denoted by a unique identifier (e.g., SAMPLE_1) and associated label text. 

```
<?xml version='1.0' encoding='UTF-8'?>
<mwt xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner#">
<template><z:sample ids="%1">%0</z:sample></template>

<t p1="SAMPLE_1">cancer</t>
<t p1="SAMPLE_2">zyx</t>
<t p1="SAMPLE_3">AGPAT3</t>
<t p1="SAMPLE_3">1-acyl-sn-glycerol-3-phosphate acyltransferase gamma</t>
<t p1="SAMPLE_4">+ delta cadinene synthase isozyme C2</t>
<t p1="SAMPLE_5">cancer</t>
<t p1="SAMPLE_6">Parkinson's disease</t>
<t p1="SAMPLE_7">a reply to Smith &amp; Weist</t>
<t p1="SAMPLE_8">[Autopsies</t>
<t p1="SAMPLE_9">dead]</t>
<t p1="SAMPLE_10">protein-serine/threonine</t>
<t p1="SAMPLE_11">"AMBAR"</t>
<t p1="SAMPLE_12">p &lt; 0.001</t>
<t p1="SAMPLE_13">α-synuclein-containing</t>

<template>%0</template>
<r><z:[^>]*>(.*</z)!:[^>]*></r>
</mwt>
```

When preparing for annotation, the [Whatizit/monq](http://haraldki.github.io/monqjfa/monqApiDoc/index.html) tool integrates regular expressions into the dictionary. These expressions transform terms into a standardized format for effective annotation. Special characters like & and < are recognized in both their encoded and non-encoded forms, however, converting them into their encoded form ensures a valid XML format. The conversion needed for such special characters is as shown below:

```
< --> &lt;
> --> &gt;
& --> &amp;
" --> &quot;
' --> &apos;
```

For a more detailed explanation on the creation of dictionaries and incorporation of regular expressions by Whatizit, please have a look [here](/docs/create_dictionary.md).


### 2. Preprocessing and Annotating XML Files

The preprocessing of input and annotated output files involves adjustments to accommodate special characters and ensure proper XML annotation. The process can be seen as consisting of three stages:

#### Step 1: Formatting Input XML Files
In the first stage, the input XML file is formatted by replacing escaped special characters with their original forms using the sed Linux command. This results in an invalid XML file but aids in recognizing terms containing such characters.
#### Step 2: Annotating XML Files
In the second stage, the formatted input XML files are annotated using the Whatizit tool, leading to an invalid annotated XML file with special characters in their original form.
#### Step 3: Formatting Annotated Output XML Files
The third stage handles two sub-stages of formatting. Firstly, it involves escaping less than ('<') characters followed by alphabets or periods using Regular Expressions to ensure compatibility with XML parsers.

Secondly, the annotated XML output is modified into valid XML format, and special characters are replaced with their corresponding encoded forms using the BeautifulSoup4 XML parser.





### 3. Creation of TF-IDF Vectors

In order to evaluate how relevant a word (MeSH term) is to a document (annotated XML file) in a collection of documents (RELISH corpus), we make use of the statistical measure of TF-IDF (term frequency-inverse document frequency).

The creation of the tf-idf matrices using our [code](/code/document-profiles/tfidf_matrix.py) is done in two main steps. The initial step involves preparing the TF matrix, which tallies the frequency of MeSH terms within each annotated XML file. This matrix aids in understanding the occurrence of MeSH terms in documents. Subsequently, the TF-IDF matrix is generated, considering the frequency of MeSH terms across the entire corpus. The TF-IDF values are calculated based on the product of TF and IDF (inverse document frequency) measures. The resulting matrices offer insights into term importance across the corpus.

To execute the code, two parameters are required: the file path to the Whatizit annotated XML files and a Bioportal-like CSV corresponding to a controlled vocabulary (MeSH in our case). The output includes two binary files storing the TF and TF-IDF matrices. 

A detailed definition of the TF, IDF and TF-IDF calculation can be found [here](/docs/tfidf.md).



### 4. Calculation of Cosine Similarity

To assess the similarity between two documents within the RELISH corpus, we employ the Cosine Similarity metric. This process enables the generation of a 4-column matrix containing cosine similarity scores for existing pairs of PMIDs within our corpus by calculating the cosine scores using the TF-IDF vectors. 



### 5. Evaluation


#### Precision@N
In order to evaluate the effectiveness of this approach, we make use of Precision@N. Precision@N measures the precision of retrieved documents at various cutoff points (N).We generate a Precision@N matrix for existing pairs of documents within the RELISH corpus, based on the original RELISH JSON file. The code determines the number of true positives within the top N pairs and computes Precision@N scores. The result is a Precision@N matrix with values at different cutoff points, including average scores. For detailed insights into the algorithm, please refer to this [documentation](https://github.com/zbmed-semtec/medline-preprocessing/tree/main/code/Precision%40N_existing_pairs).

#### nDCG@N
Another metric used is the nDCG@N (normalized Discounted Cumulative Gain). This ranking metric assesses document retrieval quality by considering both relevance and document ranking. It operates by using a TSV file containing relevance and cosine similarity scores, involving the computation of DCG@N and iDCG@N scores. The result is an nDCG@N matrix for various cutoff values (N) and each PMID in the corpus, with detailed information available in the [documentation](https://github.com/zbmed-semtec/medline-preprocessing/tree/main/code/Evaluation).

---

## Getting Started

To get started with this project, follow these steps:

### Step 1: Clone the Repository
First, clone the repository to your local machine using the following command:

###### Using HTTP:

```
git clone https://github.com/zbmed-semtec/whatizit-dictionary-ner.git
```

###### Using SSH:
Ensure you have set up SSH keys in your GitHub account.

```
git clone git@github.com:zbmed-semtec/whatizit-dictionary-ner.git
```

### Step 2: Create a virtual environment and install dependencies

To create a virtual environment within your repository, run the following command:

```
python3 -m venv .venv 
source .venv/bin/activate   # On Windows, use '.venv\Scripts\activate' 
```

To confirm if the virtual environment is activated and check the location of yourPython interpreter, run the following command:

```
which python    # On Windows command prompt, use 'where python'
                # On Windows PowerShell, use 'Get-Command python'
```
The code is stable with python 3.6 and higher. The required python packages are listed in the requirements.txt file. To install the required packages, run the following command:

```
pip install -r requirements.txt
```

To deactivate the virtual environment after running the project, run the following command:

```
deactivate
```

### Step 3: Creating Dictionary

The [code](/code/create-dictionary/) provided in the repository enables the creation of dictionaries for Whatizit. It accepts inputs in the form of Bioportal-like CSV or RDF files corresponding to controlled vocabularies. The code for parsing and creating a MWT dictionary using a CSV can be found [here](/code/create-dictionary/parse_csv.py) and using a RDF/TTL can be found [here](/code/create-dictionary/parser.py). The outcome is an MWT file following Whatizit's specifications. The code handles the exclusion of obsolete terms from the output MWT dictionary and logs them in an obsolete.log file. The code also handles the conversion of special characters as mentioned above. 

**Using CSV**

```
python3 code/create_dictionary/parse_csv.py [-i INPUT] [-o OUTPUT] [-v VOCAB]
```
You must pass the following four arguments:

+ -i/ --input : File path to the vocabulary CSV file.
+ -o/ --output : File path to the output MWT file.
+ -v/ --vocab : Name of the vocabulary.

**Using RDF**
```
python3 code/create_dictionary/parser.py
```

Note for RDF Input: Please remember to change the parameters in the `code/create-dictionary/Config.yaml` file based on the selected vocabulary and the desired output filepath.


### Step 4: Running Whatizit Container to Format and Annotate Text

For this stage, we make use of the dockerized version of Whatizit that focuses mainly on the automata part coming from MONQjfa, i.e., the container does not include the web-based aplication nor includes the dictionaries for text-mining that were available at EMBL-EBI. This step annotates the XML files against the MeSH vocabulary.


This [code](/code/annotation/annotate.py) handles the preprocessing, annotating and formatting of the text. A detailed explanation of the entire process can be found [here](/docs/preprocess.md). All the corresponding files and scripts needed for the process can be found in this [folder](/resources/whatizit/). 

In order to start with the annotation process, you would need to do the following:
+ Copy the [annotate.py](/code/annotation/annotate.py) script from the `code` folder inside `/resources/whatizit/monq/` folder. 
+ Move the created MWT dictionary inside `/resources/whatiztit/monq/automata/` folder.
+ Move the folder containing the annotated XMLs inside `/resources/whatizit/monq/text/` folder


The directory structure should be as follows:

```
whatizit
└───README.md
└───monq
│   └───automata
|        └─── mesh.mwt
│   └─── bin
│   └───config
|   └───doc
|   └───logging
|   └───text
        └─── [Insert XML files to be annotated here]
|   └───xslt
|   └─── # annotate.py     
└───Dockerfile
└───LICENSE
└───script.sh
```




|    | |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![Info](./docs/images/information_mark.png)    | Please note that before using the code for this process, we would need to build and run the Whatizit docker container that contains the corresponding files and script needed in order to annotate. Follow the instructions [here](docs/docker_annotate.md) in order to build and run the Docker container for the pre-processing, annotation and formatting of the output files.  


The main command to execute for this step once inside the docker container is as follows:

```
python3 annotate.py [-d DATASET] [-n NUMBER]
```

This command takes two parameters:

+ -d/ --dataset : Name of the dataset to be annotated. (RELISH)
+ -n/ --number : Number of files to annotate from the dataset at once.

### Step 5: Creating TF-IDF vectors and Computing Cosine Similarity

Once you have the formatted annotated XML files, you can start generating the TF-IDF vectors in the form of a matrix using this [code](./code/document-profiles/tfidf_matrix.py) by executing this command:

```
python3 code/document-profiles/tfidf_matrix.py [-a ANNOTATIONS PATH] [-d MESH DICT FILE] [-r RELEVANCE MATRIX] [-m MATRIX NAME]
```
You must pass the following arguments:

+ -a/ --annotations_path : Path to the folder containing the annotated XML files.
+ -d/ --mesh_dict_file : Path to the generated MeSH MWT dictionary.
+ -r/ --relevance_matrix : File path to the RELISH relevance matrix.
+ -m/ ----matrix_name : Output file path to save the cosine similarity matrix.

**NOTE:** This script computes the TF-IDF vectors and stores them in the form of a matrix and by using the same matrix computes the cosine similarity between all the RELISH relevance pairs. 

### Step 6: Precision@N
In order to calculate the Precision@N scores and execute this [script](/code/evaluation/precision.py), run the following command:

```
python3 code/evaluation/precision.py [-c COSINE FILE PATH]  [-o OUTPUT PATH]
```

You must pass the following two arguments:

+ -c/ --cosine_file_path: path to the 4-column cosine similarity existing pairs RELISH file: (tsv file)
+ -o/ --output_path: path to save the generated precision matrix: (tsv file)

For example, if you are running the code from the code folder and have the cosine similarity TSV file in the data folder, run the precision matrix creation for the first hyperparameter as:

```
python3 code/evaluation/precision.py -c data/whatizit_cosine.tsv -o data/whatizit_precision.tsv
```


### Step 7: nDCG@N
In order to calculate nDCG scores and execute this [script](/code/evaluation/calculate_gain.py), run the following command:

```
python3 code/evaluation/calculate_gain.py [-i INPUT]  [-o OUTPUT]
```

You must pass the following two arguments:

+ -i / --input: Path to the 4 column cosine similarity existing pairs RELISH TSV file.
+ -o/ --output: Output path along with the name of the file to save the generated nDCG@N TSV file.

For example, if you are running the code from the code folder and have the 4 column RELISH TSV file in the data folder, run the matrix creation for the first hyperparameter as:

```
python3 code/evaluation/calculate_gain.py -i data/whatizit.tsv -o data/whatizit_gain.tsv
```

## Documentation

Here is a detailed documentation for the following processes:

+ [Creating MWT Dictionary](/docs/create_dictionary.md)
+ [Preprocessing of Input XML files](/docs/preprocess.md)
+ [Running Whatizit Docker container and Annotating Text](/docs/docker_annotate.md)
+ [Creation of TF-IDF Vectors](/docs/tfidf.md)
