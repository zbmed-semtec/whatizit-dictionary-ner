#!/usr/bin/env python
from rdflib import Graph, RDF
from rdflib.namespace import SKOS, RDFS, OWL
from rdflib import Namespace
import yaml


class Parameters:
    """
    Class for input parameters to parse the MESH TTL file.
    Attributes
    ----------
    vocab_name : str
        Name of vocabulary.
    namespace : str
        Namespace for the mwt dictionary.
    """
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
        self.namespace = "https://github.com/zbmed-semtec/whatizit-dictionary-ner#"


class Parser(Parameters):
    """
    Class to parse the MESH TTL file, extract metadata for each MeSH vocabulary term and output a mwt dictionary.
    The dictionary consists of the MeSH ID, Preferred Label, Synonyms, CUI and Semantic Types for each term.
    Attributes
    ----------

    """
    def __init__(self, config_file):
        super().__init__(config_file)
        self.g = Graph()
        self.g.parse(self.input_file, format=self.file_type)
        self.__dictionary = self.create_dictionary()
        
    def get_dictionary(self) -> dict:
        """Returns the dictionary with IDs as keys and labels, synonyms as values.

        Returns
        ----------
        dict : dict
            Dictionary with IDs as keys and labels, synonyms as values.
        """
        return self.__dictionary

    def create_dictionary(self) -> dict:
        """Converts file into a dictionary with IDs as keys and
        labels, synonyms as values.

        Returns
        ----------
        dic : dict
            Dictionary with IDs as keys and labels, synonyms as values.
        """
        dic = {}
        umls = Namespace("http://bioportal.bioontology.org/ontologies/umls/")
        for owlClass in self.g.subjects(RDF.type, OWL.Class):
            if owlClass.startswith("http://purl.bioontology.org/ontology/MESH/"):
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

    @staticmethod
    def replace_chars(text) -> str:
        """Replaces special characters that invalidate the mwt format with the correct syntax.
        Parameters
        ----------
        text : str
            Term and the Synonyms.
        """
        text = text.replace("&", "&amp;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text

    def create_mwt_file(self) -> None:
        """Creates a MWT file from a dictionary with IDs as keys and labels, synonyms as values.
        saves the file to the output_file destination.
        """
        with open(self.output_file, 'w') as output:
            output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
            output.write('<mwt xmlns:z="{}">\n'.format(self.namespace))
            n_parameters = len(self.__dictionary[max(self.__dictionary, key=lambda v: len(self.__dictionary[v]))])
            if n_parameters > 2:
                output.write("<template><z:{} id='%1' cui='%2' sty='%3'>%0</z:{}></template>\n\n".
                             format(self.vocab_name, self.vocab_name))
            else:
                output.write("<template><z:{} id='%1'>%0</z:{}></template>\n\n".
                             format(self.vocab_name, self.vocab_name))
            
            for id, metadata in self.__dictionary.items():
                if 'cui' and 'semantic_types' in metadata:
                    cui = (", ".join(map(str, metadata["cui"]))).replace("'", "")
                    semantic_types = ", ".join(map(str, metadata["semantic_types"]))
                    metadata['label'] = self.replace_chars(metadata["label"])
                    output.write('<t p1="{}" p2="{}" p3="{}">{}</t>\n'.
                                 format(id, cui, semantic_types, metadata['label']))
                    if 'synonyms' in metadata:
                        n = 0
                        while n < len(metadata['synonyms']):
                            synonym = metadata['synonyms'][n]
                            synonym = self.replace_chars(synonym)
                            output.write('<t p1="{}" p2="{}" p3="{}">{}</t>\n'.format(id, cui, semantic_types, synonym))
                            n = n + 1
                elif "synonyms" in metadata:
                    metadata['label'] = self.replace_chars(metadata['label'])
                    output.write('<t p1="{}">{}</t>\n'.format(id, metadata['label']))
                    n = 0
                    while n < len(metadata['synonyms']):
                        synonym = metadata['synonyms'][n]
                        synonym = self.replace_chars(synonym)
                        output.write('<t p1="{}">{}</t>\n'.format(id, synonym))
                        n = n + 1
                else:
                    metadata['label'] = self.replace_chars(metadata['label'])
                    output.write('<t p1="{}">{}</t>\n'.format(id, metadata['label']))
            output.write("\n</mwt>")
        return
                

if __name__ == "__main__":
    parser = Parser("/home/ubuntu/workspace/whatizit/code/Config.yaml")
    dictionary = parser.get_dictionary()
    parser.create_mwt_file()
