# Processes supported by this code

## Creation of dictionaries for Whatizit
The creation of dictionaries for Whatizit takes as data input a Biportal-like CSV or RDF file corresponding to a controlled vocabulary as well as the name of the controlled vocabulary. The process creates an MWT file following the specification needed by Whatizit.

We do not include the terms which are obsolete from the CSV file in our output MWT dictionary. All the obsolete terms along with its corresponding metadata are logged into an obsolete.log file in the data folder.


**Example with CSV**
* Using the [EDAM CSV file](../data/input/EDAM.csv) and supposing you are running the code from within the code folder, run the dictionary creation as
```
python parse_csv.py --input ../data/input/EDAM.csv --output ../data/output/EDAM.mwt --vocab EDAM
```


You should get the same output as in the [EDAM MWT dictionary](../data/output/EDAM_csv.mwt)
