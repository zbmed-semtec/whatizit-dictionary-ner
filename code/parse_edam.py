from rdflib import Graph, RDF
from rdflib.namespace import OWL
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
        oboInOwl = Namespace("http://www.geneontology.org/formats/oboInOwl#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

        dic = {}
        for Class in self.g.subjects(RDF.type, OWL.Class):
            if str(Class).startswith("http://edamontology.org/"):
                dic[str(Class)] = {}
                for label in self.g.objects(Class, rdfs.label):
                    dic[str(Class)]["label"] = str(label)
                dic[str(Class)]["synonyms"] = []
                for synonyms in self.g.objects(Class, oboInOwl.hasExactSynonym):
                    dic[str(Class)]["synonyms"].append(str(synonyms))
                for synonyms in self.g.objects(Class, oboInOwl.hasNarrowSynonym):
                    dic[str(Class)]["synonyms"].append(str(synonyms))
                for synonyms in self.g.objects(Class, oboInOwl.hasBroadSynonym):
                    dic[str(Class)]["synonyms"].append(str(synonyms))
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
            output.write('<mwt xmlns:="{}">\n'.format(self.z))
            n_parameters = len(self.__dictionary[max(self.__dictionary, key=lambda v: len(self.__dictionary[v]))])
            if n_parameters > 2:
                output.write("<template><z:{} id='%1' cui='%2' semantics='%3'>%0</z:{}></template>\n\n".format(self.vocab_name, self.vocab_name))
            else:
                output.write("<template><z:{} id='%1'>%0</z:{}></template>\n\n".format(self.vocab_name, self.vocab_name))

            for id, metadata in self.__dictionary.items():
                metadata['label'] = self.replace_chars(metadata['label'])
                output.write('<t p1="{}">{}</t>\n'.format(id, metadata['label']))
                if 'synonyms' in metadata:
                    n = 0
                    while n < len(metadata['synonyms']):
                        synonym = metadata['synonyms'][n]
                        synonym = self.replace_chars(synonym)
                        output.write('<t p1="{}">{}</t>\n'.format(id, synonym))
                        n = n + 1
            output.write("\n</mwt>")
        return


if __name__ == "__main__":
    parser = Parser("../code/Config.yaml")
    dictionary = parser.get_dictionary()
    parser.create_mwt_file()
