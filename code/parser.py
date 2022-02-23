from rdflib import Graph, RDF
from rdflib.namespace import SKOS, RDFS, OWL
import yaml

class Parameters:
    
    def __init__(self,config_file):
        
        with open(config_file) as file:
            try:
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
                
        self.input_file = self.config['input_file_path']
        self.output_file = self.config['output_file_path']
        self.file_type = self.config['file_type']
        self.vocab_name = self.config['vocab_name']
        self.z = "https://github.com/zbmed-semtec/whatizit-dictionary-ner" # package name

class Parser(Parameters):
    
    def __init__(self,config_file):
        super().__init__(config_file)
        self.g = Graph()
        self.g.parse(self.input_file, format=self.file_type)
        self.__dictionary = self.create_dictionary()
        
    def get_dictionary(self):
        """Returns the dictionary with IDs as keys and labels, synonyms as values.

        Returns:
            dict (dict): Dictionary with IDs as keys and labels, synonyms as values.
        """
        return self.__dictionary
        

    def create_dictionary(self):
        """  file into a dictionary with IDs as keys and
        labels, synonyms as values.

        Returns:
            dic (dict): Dictionary with IDs as keys and labels, synonyms as values.

        """
        dic = {}
        for owlClass in self.g.subjects(RDF.type, OWL.Class):
            for notation in  self.g.objects(owlClass, SKOS.notation):
                dic[str(owlClass)] = {}
            for label in self.g.objects(owlClass, SKOS.prefLabel):
                dic[str(owlClass)]["label"] = str(label)
            dic[str(owlClass)]["synonyms"] = []
            dic[str(owlClass)]["semantic_types"] = []
            for synonyms in self.g.objects(owlClass, SKOS.altLabel):
                dic[str(owlClass)]["synonyms"].append(str(synonyms))
            for semantic_types in self.g.objects(owlClass, RDFS.subClassOf):
                dic[str(owlClass)]["semantic_types"].append(str(semantic_types))
        
        return  dic

    def create_mwt_file(self):
        """creates a MWT file from a dictionary with IDs as keys and labels, synonyms as values.
        saves the file to the output_file destination.
        """
        
        with open(self.output_file, 'w') as output:
            output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            output.write('<mwt xmlns:="{}">\n'.format(self.z))
            output.write("<template><z:{} id='%1' semantics='%2'>%0</z:{}></template>\n\n".format(self.vocab_name, self.vocab_name))
            
            for id, metadata in self.dictionary.items():
                line = "<t p1='{}'".format(id)
                if not metadata["semantic_types"]:
                    semantic_types=", ".join(map(str,list(metadata["semantic_types"])))
                    line = line + " p2='{}'".format(semantic_types)
                if not metadata["synonyms"]:
                    synonyms=", ".join(map(str,list(metadata["synonyms"])))
                    line = line+">{}</t>\n".format(metadata["label"]+" "+synonyms)
                else:
                    line = line+">{}</t>\n".format(metadata["label"])
                output.write(line)
            output.write("</mwt>")
        
        return
                
    


if __name__ == "__main__":
    parser = Parser("../code/Config.yaml")
    dictionary = parser.get_dictionary()
    parser.create_mwt_file()
                
    
    
    