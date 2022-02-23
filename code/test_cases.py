from itertools import count
import unittest
import re
from parse_csv import CSVParser
from parser import Parser

class TestCases(unittest.TestCase):
    
    def __init__(self):
        pass

    def test_namespace(self):
        """Tests for the namespace of the mwt dictionary file."""

        CSVParser('../data/input/sample_MESH.csv', '../data/output/test1.mwt', 'MESH')
        with open('../data/output/test1.mwt', 'r') as test_output:
            header = test_output.read().splitlines()[:3]
            self.assertEqual(header[0] == "<?xml version='1.0' encoding='UTF-8'?>")
            self.assertEqual(header[1] == '<mwt xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner/">')
            self.assertEqual(header[2] == "<template><z:MESH id='%1' cui='%2' semantics='%3'>%0</z:MESH></template>")

    def test_labels(self):
        """Checks if all vocabulary terms are included in both output dictionaries, ttl and csv."""

        CSVParser('../data/input/sample_MESH.csv', '../data/output/test1.mwt', 'MESH')
        Parser("../code/Config.yaml")
        with open('../data/output/test1.mwt', 'r') as test_output1, open('../data/output/test2.mwt', 'r') as test_output2:
            lines_csv = test_output1.read().splitlines()[4:-1]
            lines_ttl = test_output2.read().splitlines()[4:-1]
        labels_csv = set()
        labels_ttl = set()
        for line in lines_csv:
            label = re.search('(?<=>)(.*?)(?=</)', line)
            labels_csv.add(label.group())
        for line in lines_ttl:
            label = re.search('(?<=>)(.*?)(?=</)', line)
            labels_ttl.add(label.group())
        self.assertEqual(set(labels_csv) == set(labels_ttl))

    def test_countlines(self):
        """Checks if the number of vocabulary terms is the same in both output dictionaries, ttl and csv."""
        with open('../data/output/test1.mwt', 'r') as f1, open('../data/output/test2.mwt', 'r') as f2:
            count1 = len(f1.readlines()[4:-1])
            count2 = len(f2.readlines()[4:-1])
        self.assertEqual(count1, count2)
            
            

if __name__ == '__main__':
    unittest.main()

