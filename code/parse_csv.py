#!/usr/bin/env python
import os
import sys
import csv
import argparse
import pandas as pd
import logging

csv.field_size_limit(sys.maxsize)

if not os.path.exists("../data/logging"):
    os.makedirs("../data/logging")


logging.basicConfig(filename='../data/logging/obsolete.log', filemode='w', level=logging.DEBUG)


class CSVParser:
    def __init__(self, input_file: str, output_file: str, vocab: str):
        self.input_file = input_file
        self.output_file = output_file
        self.vocab = vocab
        self.metadata = self.get_metadata()

    def get_metadata(self) -> dict:
        """Parses the csv file and returns a dictionary of Class IDs with the corresponding metadata.
        Obsolete terms are logged into a log file.
        Returns :
                metadata : Dictionary of metadata
                Class ID : {"Term" : Preferred Label,
                            "Synonyms" : Synonym(s),
                            "CUI: Concept identifier(s),
                            "Semantic Types" : Semantic Type UMLS property
                            }
        """
        data = pd.read_csv(self.input_file, engine='python')
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

    def replace_chars(self, text):
        """Replaces special characters that invalidate the mwt format with the correct syntax."""
        text = text.replace("&", "&amp;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    def write_mwt(self):
        """Takes the data from the metadata dictionary and writes it to an output mwt file"""
        with open(self.output_file, 'w') as output:
            output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            output.write('<mwt xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner">\n')
            n_parameters = len(self.metadata[max(self.metadata, key=lambda v:len(self.metadata[v]))])
            if n_parameters > 2:
                output.write("<template><z:{} id='%1' cui='%2' semantics='%3'>%0</z:{}></template>\n\n".format(self.vocab, self.vocab))
            else:
                output.write("<template><z:{} id='%1'>%0</z:{}></template>\n\n".format(self.vocab, self.vocab))

            for class_id, metadata in self.metadata.items():
                if "CUI" and "Semantic Types" in metadata:
                    metadata['Term'] = self.replace_chars(metadata['Term'])
                    output.write('<t p1="{}" p2="{}" p3="{}">{}</t>\n'.format(class_id, metadata['CUI'], metadata['Semantic Types'], metadata['Term']))
                    if "Synonyms" in metadata:
                        n = 0
                        while n < len(metadata['Synonyms']):
                            synonym = metadata['Synonyms'][n]
                            synonym = self.replace_chars(synonym)
                            output.write('<t p1="{}" p2="{}" p3="{}">{}</t>\n'.format(class_id, metadata['CUI'], metadata['Semantic Types'], synonym))
                            n = n + 1
                elif "Synonyms" in metadata:
                    metadata['Term'] = self.replace_chars(metadata['Term'])
                    output.write('<t p1="{}">{}</t>\n'.format(class_id, metadata['Term']))
                    n = 0
                    while n < len(metadata['Synonyms']):
                        synonym = metadata['Synonyms'][n]
                        synonym = self.replace_chars(synonym)
                        output.write('<t p1="{}">{}</t>\n'.format(class_id, synonym))
                        n = n + 1
                else:
                    metadata['Term'] = self.replace_chars(metadata['Term'])
                    output.write('<t p1="{}">{}</t>\n'.format(class_id, metadata['Term']))
            output.write("\n</mwt>")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Path for input csv file")
    parser.add_argument("--output", type=str, help="Path for output mwt file")
    parser.add_argument("--vocab", type=str, help="Namespace for controlled vocabulary for mwt file")
    args = parser.parse_args()
    csv_parser = CSVParser(args.input, args.output, args.vocab)
    csv_parser.write_mwt()

