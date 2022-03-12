from rdflib import Graph, RDF, Namespace
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
    
    def replace_chars(self, text):
        """Replaces special characters that invalidate the mwt format with the correct syntax."""
        text = text.replace("&", "&amp;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        return text
    
    def create_namespace(self, namespace:str):
        """Creates a namespace from the given string."""
        return Namespace(namespace)
    
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
            for semantic_types in self.g.objects(owlClass, RDFS.subClassOf):
                dic[str(owlClass)]["semantic_types"].append(str(semantic_types))
            for cui in self.g.objects(owlClass, umls.cui):
                dic[str(owlClass)]["cui"].append(str(cui))
        
        
        for namespace in self.config["namespaces"].values():
            for lst in self.config["namespaces"][str(namespace)].values():
                