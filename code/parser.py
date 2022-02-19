from rdflib import Graph
from rdflib.namespace import SKOS
import yaml


class Parser:
    
    def __init__(self,config_file):
        
        with open(config_file) as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
                
        self.input_file = config['input_file_path']
        self.output_file = config['output_file_path']
        self.file_type = config['file_type']
        self.dictionary = self.create_dictionary()
        
    def get_dictionary(self):
        """Returns the dictionary with IDs as keys and labels, synonyms as values.

        Returns:
            dict (dict): Dictionary with IDs as keys and labels, synonyms as values.
        """
        return self.dictionary
        

    def create_dictionary(self):
        """ Converts a TTL file into a dictionary with IDs as keys and
        labels, synonyms as values.

        Args:
            ttl_file (String): Path to the TTL file.

        Returns:
            ttl_dic (dict): Dictionary with IDs as keys and labels, synonyms as values.
            ttl_dic = {"id": ["label", "synonym1", "synonym2", ...]}
        """
        ttl_dic = {}
        g = Graph()
        g.parse(self.input_file, format=self.file_type)
        
        for id in g.subject_objects(SKOS.notation):
            for label in g.subject_objects(SKOS.prefLabel):
                ttl_dic[id[0]] = [str(label[1])]
            for synonym in g.subject_objects(SKOS.altLabel):
                ttl_dic[id[0]].append(str(synonym[1]))
        
        return ttl_dic

    def create_mwt_file(self):
        """creates a MWT file from a dictionary with IDs as keys and labels, synonyms as values.
        saves the file to the output_file destination.

        Args:
            dict (dict): Dictionary with IDs as keys and labels, synonyms as values.
            output_file (str): Path to the output file.
        """
        
        with open(self.output_file, 'w') as output:
            output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            output.write('<mwt xmlns:z="http://purl.bioontology.org/ontology/MESH/">\n')
            output.write("<template><z:MESH id='%1'>%0</z:MESH></template>\n\n")
            
            for id, metadata in self.dictionary.items():
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
    parser = Parser("../code/Config.yaml")
    dictionary = parser.get_dictionary()
    print(list(dictionary.keys())[0])
    print(list(dictionary.values())[0])
                
    
    
    