#!/usr/bin/env python
import os
import argparse
import pandas as pd
import logging


if not os.path.exists("../data/logging"):
    os.makedirs("../data/logging")


logging.basicConfig(filename='../data/logging/obsolete.log', filemode='w', level=logging.DEBUG)


def get_metadata(input_file):
    """Parses the csv file and returns a dictionary of Class IDs with the corresponding metadata.
    Obsolete terms are logged into a log file.
    Input : csv file
    Output : metadata -> Dictionary of metadata
             Class ID : {"Term" : Preferred Label, "Synonyms" : Synonyms}
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
    return metadata


def write_mwt(metadata_dict, output_filename):
    """Takes the data from the metadata dictionary and writes it to an output mwt file
    Input: metadata_dict -> Dictionary of metadata
           output_filename -> Output file path
    Output : MWT file
    """
    with open(output_filename, 'w') as output:
        output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        output.write('<mwt xmlns:z="http://purl.bioontology.org/ontology/MESH/">\n')
        output.write("<template><z:MESH id='%1'>%0</z:MESH></template>\n\n")

        for class_id, metadata in metadata_dict.items():
            output.write('<t p1="{}">{}</t>\n'.format(class_id, metadata['Term']))
            if "Synonyms" in metadata:
                n = 0
                while n < len(metadata['Synonyms']):
                    synonym = metadata['Synonyms'][n]
                    output.write('<t p1="{}">{}</t>\n'.format(class_id, synonym))
                    n = n + 1
        output.write("\n</mwt>")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Path for input csv file")
    parser.add_argument("--output", type=str, help="Path for output mwt file")
    args = parser.parse_args()
    meta = get_metadata(args.input)
    write_mwt(meta, args.output)
