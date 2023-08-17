# **whatizit-dictionary-ner**: A Dictionary-based NER Approach for TF-IDF Vector Generation using Whatizit tool

This repository contains code and documentation for a dictionary-based Named Entity Recognition (NER) approach to generate TF-IDF vectors using the [Whatizit](https://academic.oup.com/bioinformatics/article/24/2/296/227269?login=true) annotation tool. It involves preparing input XML files and annotating them using Whatizit against a controlled vocabulary, in our case, the [Medical Subject Headings](https://www.nlm.nih.gov/mesh/meshhome.html) (MeSH) ontology. 

Whatizit is a text processing system that allows you to do textmining tasks on text. Whatizit was created by the Rebholz Research Group at EMBL-EBI. It is based on MONQjfa, a non-deterministic and deterministic dinite automata for Java. In our approach, we specifically make use of a [Dockerized version of Whatizit](https://github.com/zbmed-semtec/simple-whatizit-docker). 

# Data Input: XML Files

The approach utilizes preprocessed [XML files](https://github.com/zbmed-semtec/relish-preprocessing/tree/main/data/output/sample-files/xml) obtained from the [RELISH preprocessing pipeline](https://github.com/zbmed-semtec/relish-preprocessing/tree/main). These XMLs are structured biomedical texts resulting from initial processing, ensuring consistent formatting and content organization. While these files are not annotated with specific medical terms at this stage, they provide the groundwork for the NER process. The processes described in the following README involve using the Whatizit annotation tool for these preprocessed XMLs to identify and tag medical terms as per the MeSH vocabulary, eventually leading to the generation of TF-IDF vectors that capture the significance of these terms within the context of the biomedical texts.

# Process
 The following section outlines the primary processes applied to the input XML files of the RELISH dataset in order to generate the TF-IFD vectors.

# 1. Dictionary Creation

The initial step in annotating text involves the creation of a dictionary that serves as the reference for identifying expressions within the text and associating them with concepts from a controlled vocabulary. This process starts by selecting the desired vocabulary to support. For each preferred and alternative label within the vocabulary, an entry is crafted in the dictionary.

The creation of dictionaries for Whatizit takes as data input a Biportal-like CSV or RDF file corresponding to a controlled vocabulary. We do not include the terms which are obsolete from the CSV file in our output MWT dictionary.

The generated dictionary follows a MWT format (XML-like structure) as required by Whatizit and is illustrated in the example provided below. Notably, the dictionary may include certain XML special characters (e.g., & < >), which may necessitate special handling. The XML-like format encompasses a template and individual entries, each denoted by a unique identifier (e.g., SAMPLE_1) and associated label text. 

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

The [code](/code/create-dictionary/) provided in the repository enables the creation of dictionaries for Whatizit. It accepts inputs in the form of Bioportal-like CSV or RDF files corresponding to controlled vocabularies. The code for parsing and creating a MWT dictionary using a CSV can be found [here](/code/create-dictionary/parse_csv.py) and using a RDF/TTL can be found [here](/code/create-dictionary/parser.py). The outcome is an MWT file following Whatizit's specifications. The code handles the exclusion of obsolete terms from the output MWT dictionary and logs them in an obsolete.log file. The code also handles the conversion of special characters as mentioned above. For a more detailed explanation on the creation of dictionaries and incorporation of regular expressions by Whatizit, please have a look [here](/docs/create_dictionary.md).

# 2. Preprocessing Input and Output Files

The preprocessing of input and annotated output files involves adjustments to accommodate special characters and ensure proper XML annotation. The process can be seen as consisting of three stages:

## Formatting Input XML Files
In the first stage, the input XML file is formatted by replacing escaped special characters with their original forms using the sed Linux command. This results in an invalid XML file but aids in recognizing terms containing such characters.
## Annotating XML Files
In the second stage, the formatted input XML files are annotated using the Whatizit tool, leading to an invalid annotated XML file with special characters in their original form.
## Formatting Annotated Output XML Files
The third stage handles two sub-stages of formatting. Firstly, it involves escaping less than ('<') characters followed by alphabets or periods using Regular Expressions to ensure compatibility with XML parsers.

Secondly, the annotated XML output is modified into valid XML format, and special characters are replaced with their corresponding encoded forms using the BeautifulSoup4 XML parser.

The corresponding code script handles all of the above mentioned three stages and can be found [here](/code/annotate/annotate.py). A detailed explanation of the entire process can be found [here](/docs/preprocess.md).


|    | |
|----|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ![Info](./docs/images/information_mark.png)    | Please note that before using the code for this process, we would need to build and run the Whatizit docker container that contains the corresponding files and script needed in order to annotate, i.e. run the above mentioned three stage process. 

---


# 3. Running Whatizit Container and Annotating Text

In this stage, we make use of the dockerized version of Whatizit that focuses mainly on the automata part coming from MONQjfa, i.e., the container does not include the web-based aplication nor includes the dictionaries for text-mining that were available at EMBL-EBI. 

All the corresponding files and scripts needed for the process can be found in this [folder](/resources/whatizit/). In order to start with the annotation process, you would need to place the [Python script](/code/annotation/annotate.py) for annotation (as described in Stage 2) inside the monq folder as shown below. The directory structure is as follows:

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

A detailed step-by-step procedure in order to build and run the Docker container as well as to annotate the input text can be found [here](/docs/docker_annotate.md). 


# 4. Creation of TF-IDF Vectors

In order to evaluate how relevant a word (MeSH term) is to a document (annotated XML file) in a collection of documents (RELISH corpus), we make use of the statistical measure of TF-IDF (term frequency-inverse document frequency).

The creation of the tf-idf matrices using our [code](/code/document-profiles/tfidf_matrix.py) is done in two main steps. The initial step involves preparing the TF matrix, which tallies the frequency of MeSH terms within each annotated XML file. This matrix aids in understanding the occurrence of MeSH terms in documents. Subsequently, the TF-IDF matrix is generated, considering the frequency of MeSH terms across the entire corpus. The TF-IDF values are calculated based on the product of TF and IDF (inverse document frequency) measures. The resulting matrices offer insights into term importance across the corpus.

To execute the code, two parameters are required: the file path to the Whatizit annotated XML files and a Bioportal-like CSV corresponding to a controlled vocabulary (MeSH in our case). The output includes two binary files storing the TF and TF-IDF matrices. 

A detailed definition of the TF, IDF and TF-IDF calculation can be found [here](/docs/tfidf.md).

# Documentation

Please find a detailed documentation for the following processes below:

+ [Creating MWT Dictionary](/docs/create_dictionary.md)
+ [Preprocessing of Input XML files](/docs/preprocess.md)
+ [Running Whatizit Docker container and Annotating Text](/docs/docker_annotate.md)
+ [Creation of TF-IDF Vectors](/docs/tfidf.md)


# Code Implementation

+ [Creating MWT Dictionary](/code/create-dictionary/)
+ [Annotating XML files](/code/annotate/annotate.py)
+ [Creation of TF-IDF Vectors](/code/document_profiles/tfidf_matrix.py)