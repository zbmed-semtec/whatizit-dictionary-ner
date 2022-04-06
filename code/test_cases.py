from contextlib import closing
import unittest
import re
from rdflib import Graph
from parse_csv import CSVParser
from parser import Parser


class TestCases(unittest.TestCase):
    
    def setUp(self):
        self.parser = Parser("../code/Config.yaml")
        self.csv_parser = CSVParser('../data/input/sample_MESH.csv', '../data/output/test1.mwt', 'MESH')
        self.test_file_1 = '../data/output/mesh.mwt'
        self.test_file_2 = '../data/output/MESH_ttl2mwt.mwt'

    def test_namespace(self):
        """Tests for the namespace of the mwt dictionary file."""
        
        def testing(file_name):
            with open(file_name, 'r') as test_output:
                lines = test_output.read().splitlines()
                header = lines[:3]
                closing_tag = lines[-1]
                
                self.assertEqual(header[0], "<?xml version='1.0' encoding='UTF-8'?>")
                self.assertEqual(header[1], '<mwt xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner">')
                self.assertEqual(header[2], "<template><z:MESH id='%1' cui='%2' semantics='%3'>%0</z:MESH></template>")
                self.assertEqual(closing_tag, '</mwt>')
        testing(self.test_file_1)
        testing(self.test_file_2)

    def test_labels(self):
        """Checks if all vocabulary terms are included in both output dictionaries, ttl and csv."""

        with open(self.test_file_1, 'r') as test_output1, open(self.test_file_2, 'r') as test_output2:
            lines_csv = test_output1.read().splitlines()[4:-2]
            lines_ttl = test_output2.read().splitlines()[4:-2]
        labels_csv = set()
        labels_ttl = set()
        for line in lines_csv:
            label = re.search('(?<=>)(.*?)(?=</)', line)
            labels_csv.add(label.group())
        for line in lines_ttl:
            label = re.search('(?<=>)(.*?)(?=</)', line)
            labels_ttl.add(label.group())
        self.assertEqual(set(labels_csv), set(labels_ttl))

    def test_countlines(self):
        """Checks if the number of vocabulary terms is the same in both output dictionaries, ttl and csv."""
        with open('../data/output/mesh.mwt', 'r') as f1, open('../data/output/MESH_ttl2mwt.mwt', 'r') as f2:
            count1 = len(f1.readlines()[4:-1])
            count2 = len(f2.readlines()[4:-1])
        self.assertEqual(count1, count2)
        
    def test_parameters(self):
        """Checks if the input file, output file and vocabulary name is empty."""
        self.assertIsNotNone(self.parser.input_file)
        self.assertIsNotNone(self.parser.output_file)
        self.assertIsNotNone(self.parser.vocab_name)
        self.assertIsNotNone(self.parser.file_type)
        self.assertIsNotNone(self.parser.z)
        self.assertIsNotNone(self.parser.get_dictionary(), "Dictionary is empty")
        self.assertIsInstance(self.parser.g, Graph)
        self.assertIsNotNone(self.csv_parser.input_file)
        self.assertIsNotNone(self.csv_parser.output_file)
        self.assertIsNotNone(self.csv_parser.vocab)
        self.assertIsNotNone(self.csv_parser.metadata, "Dictionary is empty")


if __name__ == '__main__':
    unittest.main()
