import unittest
import re
from parse_csv import CSVParser
from parser import Parser

class TestCases(unittest.TestCase):

    def test_namespace(self):
        """Tests for the namespace of the mwt dictionary file."""

        CSVParser('../data/input/sample_MESH.csv', '../data/output/test1.mwt', 'MESH')
        with open('../data/output/test1.mwt', 'r') as test_output:
            header = test_output.read().splitlines()[:3]
            assert header[0] == "<?xml version='1.0' encoding='UTF-8'?>"
            assert header[1] == '<mwt xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner/">'
            assert header[2] == "<template><z:MESH id='%1' cui='%2' semantics='%3'>%0</z:MESH></template>"

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
        assert set(labels_csv) == set(labels_ttl)

    def test_count(self):
        # Add test for count

if __name__ == '__main__':
    unittest.main()

