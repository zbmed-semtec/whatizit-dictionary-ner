from rdflib import Graph, RDF
from rdflib.namespace import SKOS, RDFS, OWL
from rdflib import Namespace
import yaml


class Parameters:
    
    def __init__(self, config_file):
        
        with open(config_file) as file:
            try:
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
                
        self.input_file = self.config['input_file_path']
        self.output_file = self.config['output_file_path']
        self.file_type = self.config['file_type']
        self.vocab_name = self.config['vocab_name']
        self.z = "https://github.com/zbmed-semtec/whatizit-dictionary-ner"  # package name


class Parser(Parameters):
    
    def __init__(self, config_file):
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
        umls = Namespace("http://bioportal.bioontology.org/ontologies/umls/")
        for owlClass in self.g.subjects(RDF.type, OWL.Class):
            for notation in self.g.objects(owlClass, SKOS.notation):
                dic[str(owlClass)] = {}
            for label in self.g.objects(owlClass, SKOS.prefLabel):
                dic[str(owlClass)]["label"] = str(label)
            dic[str(owlClass)]["synonyms"] = []
            dic[str(owlClass)]["semantic_types"] = []
            dic[str(owlClass)]["cui"] = []
            for synonyms in self.g.objects(owlClass, SKOS.altLabel):
                dic[str(owlClass)]["synonyms"].append(str(synonyms))
            for semantic_types in self.g.objects(owlClass, umls.hasSTY):
                dic[str(owlClass)]["semantic_types"].append(str(semantic_types))
            for cui in self.g.objects(owlClass, umls.cui):
                dic[str(owlClass)]["cui"].append(str(cui))
        return dic

    def replace_chars(self, text):
        """Replaces special characters that invalidate the mwt format with the correct syntax."""
        text = text.replace("&", "&amp;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    def create_mwt_file(self):
        """creates a MWT file from a dictionary with IDs as keys and labels, synonyms as values.
        saves the file to the output_file destination.
        """
        
        with open(self.output_file, 'w') as output:
            output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            output.write('<mwt xmlns:z="{}">\n'.format(self.z))
            n_parameters = len(self.__dictionary[max(self.__dictionary, key=lambda v: len(self.__dictionary[v]))])
            if n_parameters > 2:
                output.write("<template><z:{} id='%1' cui='%2' semantics='%3'>%0</z:{}></template>\n\n".format(self.vocab_name, self.vocab_name))
            else:
                output.write("<template><z:{} id='%1'>%0</z:{}></template>\n\n".format(self.vocab_name, self.vocab_name))
            
            for id, metadata in self.__dictionary.items():
                line = '<t p1="{}"'.format(id)
                if 'cui' in metadata:
                    cui = ", ".join(map(str, list(metadata["cui"])))
                    line = line + " p2='{}'".format(cui)
                elif 'semantic types' in metadata:
                    semantic_types = ", ".join(map(str, list(metadata["semantic_types"])))
                    line = line + " p3='{}'".format(semantic_types)
                metadata['label'] = self.replace_chars(metadata["label"])
                line = line + ">{}</t>\n".format(metadata["label"])
                if 'synonyms' in metadata:
                    line = '<t p1="{}"'.format(id)
                    n = 0
                    while n < len(metadata['synonyms']):
                        synonym = metadata['synonyms'][n]
                        synonym = self.replace_chars(synonym)
                        output.write('<t p1="{}">{}</t>\n'.format(id, synonym))
                        n = n + 1
                    metadata['label'] = self.replace_chars(metadata["label"])
                    line = line + ">{}</t>\n".format(metadata["label"])
                output.write(line)
            output.write("\n</mwt>")
        
        return
                

if __name__ == "__main__":
    parser = Parser("../code/Config.yaml")
    dictionary = parser.get_dictionary()
    parser.create_mwt_file()