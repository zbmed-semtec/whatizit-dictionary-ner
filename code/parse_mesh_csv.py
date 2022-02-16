#!/usr/bin/env python

import pandas as pd


def mesh_csv_to_dict(file):
    """Parses MESH csv file and returns a dictionary of MESH IDs with metadata
    Input : MESH csv file
    Output : MESH Dictionary
            MESH ID : {"Term" : Preferred Label, "Synonyms" : Synonyms}
    """
    data = pd.read_csv(file, usecols=['Class ID', 'Preferred Label', 'Synonyms'])
    data['Class ID'] = [id.split("/MESH/")[::-1][0] for id in data['Class ID']]
    mesh_vocab_dict = dict()
    for i in range(len(data)):
        mesh_vocab_dict[data['Class ID'].iloc[i]] = {'Term': data['Preferred Label'].iloc[i]}
        if pd.isnull(data['Synonyms'].iloc[i]) is False:
            mesh_vocab_dict[data['Class ID'].iloc[i]]['Synonyms'] = data['Synonyms'].iloc[i].split("|")
    return mesh_vocab_dict


def mwt_dict(mesh_dict, output_filename):
    """Converts the MESH dictionary into a mwt file and writes it to the output file
    Input: MESH dict
    Output : mwt dictionary file
    """
    with open(output_filename, 'w') as output:
        output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        output.write('<mwt xmlns:z="http://purl.bioontology.org/ontology/MESH/">\n')
        output.write("<template><z:MESH id='%1'>%0</z:MESH></template>\n\n")

        for mesh_id, metadata in mesh_dict.items():
            output.write('<t p1="{}">{}</t>\n'.format(mesh_id, metadata['Term']))
            if "Synonyms" in metadata:
                n = 0
                while n < len(metadata['Synonyms']):
                    synonym = metadata['Synonyms'][n]
                    output.write('<t p1="{}">{}</t>\n'.format(mesh_id, synonym))
                    n = n + 1
        output.write("\n</mwt>")
    return


# mesh_dict = mesh_csv_to_dict("../code/MESH.csv")
# mwt_dict(mesh_dict, "mesh.mwt")
