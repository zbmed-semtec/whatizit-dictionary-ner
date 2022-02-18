#!/usr/bin/env python
import os
import argparse
import pandas as pd
import logging


if not os.path.exists("../data/logging"):
    os.makedirs("../data/logging")


logging.basicConfig(filename='../data/logging/obsolete.log', filemode='w', level=logging.DEBUG)


def get_metadata(input_file: str) -> dict:
    """Parses the csv file and returns a dictionary of Class IDs with the corresponding metadata.
    Obsolete terms are logged into a log file.
    Input : csv file
    Output : metadata -> Dictionary of metadata
             Class ID : {"Term" : Preferred Label,
                        "Synonyms" : Synonym(s),
                        "CUI: Concept identifier(s),
                        "Semantic Types" : Semantic Type UMLS property
                        }
    """
    data = pd.read_csv(input_file, low_memory=False)
    if True in data['Obsolete'].unique():
        pos = data.index[data['Obsolete'] == True]
        for ind in pos:
            logging.info((", ".join(str(x) for x in data.iloc[ind])).replace("nan", ''))
        data.drop(data.index[pos], inplace=True)
    metadata = dict()
    for i in range(len(data)):
        metadata[data['Class ID'].iloc[i]] = {'Term': data['Preferred Label'].iloc[i]}
        if pd.isnull(data['Synonyms'].iloc[i]) is False:
            metadata[data['Class ID'].iloc[i]]['Synonyms'] = data['Synonyms'].iloc[i].split("|")
        if pd.isnull(data['CUI'].iloc[i]) is False:
            metadata[data['Class ID'].iloc[i]]['CUI'] = data['CUI'].iloc[i].replace("|", ", ")
        if pd.isnull(data['Semantic Types'].iloc[i]) is False:
            metadata[data['Class ID'].iloc[i]]['Semantic Types'] = data['Semantic Types'].iloc[i].replace("|", ", ")
    return metadata


def write_mwt(metadata_dict: dict, output_filename: str, vocab: str):
    """Takes the data from the metadata dictionary and writes it to an output mwt file
    Input: metadata_dict -> Dictionary of metadata
           output_filename -> Output file path
    Output : MWT file
    """
    with open(output_filename, 'w') as output:
        output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        output.write('<mwt xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner/">\n')
        output.write("<template><z:{} id='%1' cui='%2' semantics='%3'>%0</z:{}></template>\n\n".format(vocab, vocab))

        for class_id, metadata in metadata_dict.items():
            if "CUI" and "Semantic Types" in metadata:
                output.write('<t p1="{}" p2="{}" p3="{}">{}</t>\n'.format(class_id, metadata['CUI'], metadata['Semantic Types'], metadata['Term']))
                if "Synonyms" in metadata:
                    n = 0
                    while n < len(metadata['Synonyms']):
                        synonym = metadata['Synonyms'][n]
                        output.write('<t p1="{}" p2="{}" p3="{}">{}</t>\n'.format(class_id, metadata['CUI'], metadata['Semantic Types'], synonym))
                        n = n + 1
            elif "Synonyms" in metadata:
                n = 0
                while n < len(metadata['Synonyms']):
                    synonym = metadata['Synonyms'][n]
                    output.write('<t p1="{}">{}</t>\n'.format(class_id, synonym))
                    n = n + 1
            else:
                output.write('<t p1="{}">{}</t>\n'.format(class_id, metadata['Term']))
        output.write("\n</mwt>")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Path for input csv file")
    parser.add_argument("--output", type=str, help="Path for output mwt file")
    parser.add_argument("--vocab", type=str, help="Namespace for controlled vocabulary for mwt file")
    args = parser.parse_args()
    meta = get_metadata(args.input)
    write_mwt(meta, args.output, args.vocab)
