from rdflib import Graph
from rdflib.namespace import SKOS

def ttl_to_dictionary(ttl_file:str):
    """ Converts a TTL file into a dictionary with IDs as keys and
    labels, synonyms as values.

    Args:
        ttl_file (String): Path to the TTL file.

    Returns:
        ttl_dic (dict): Dictionary with IDs as keys and labels, synonyms as values.
    """
    ttl_dic = {}
    g = Graph()
    g.parse(ttl_file, format="ttl")
    
    for id in g.subject_objects(SKOS.notation):
        for label in g.subject_objects(SKOS.prefLabel):
            ttl_dic[id[1]] = [str(label[1])]
        for synonym in g.subject_objects(SKOS.altLabel):
            ttl_dic[id[1]].append(str(synonym[1]))
    
    return ttl_dic

def create_mwt_file(dict, output_file):
    """_summary_

    Args:
        dict (_type_): _description_
        output_file (_type_): _description_
    """
    
    with open(output_file, 'w') as output:
        output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        output.write('<mwt xmlns:z="http://purl.bioontology.org/ontology/MESH/">\n')
        output.write("<template><z:MESH id='%1'>%0</z:MESH></template>\n\n")
        
        for id, metadata in dict.items():
            output.write('<t p1="{}">{}</t>\n'.format(id, metadata[0]))
            if len(metadata) > 1:
                n = 1
                while n < len(metadata):
                    synonym = metadata[n]
                    output.write('<t p1="{}">{}</t>\n'.format(id, synonym))
                    n = n + 1
        output.write("\n</mwt>")
    return
    


if __name__ == "__main__":
    ttl_dic = ttl_to_dictionary("../data/input/AI-RHEUM.ttl")
    create_mwt_file(ttl_dic, "../data/output/AI-RHEUM.mwt")
    
                
    
    
    