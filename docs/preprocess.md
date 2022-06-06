# Preprocessing input and output files

In order to accommodate the special characters found in the input files and to correctly annotate the XML files, you need to perform certain modifications to the input XML file and the annotated XML file output. 

The pipeline for the modifications that need to be done is as follows:

#### 1. Format input XML file 
 Modify the input XML files by unescaping the escaped special characters. You need to replace the HTML encoding of the special characters to its original form.
 The conversion should be as follows:

    &lt; --> < 
    &gt: --> > 
    &amp; --> &

This will result in an invalid XML file but is necessary in order for whatizit/monq to recognize terms that include such special characters.
Our pipeline makes use of the ```sed``` linux command to replace the encoded version for the plain version. 

```sed 's/&lt;/</g;s/&gt;/>/g;s/&amp;/\&/g' {input_filename} > {formatted_input_filename}```

#### 2. Annotate files
Annotate the formatted input XML files with the dictionary of your choice using the whatizit tool. This will also result in an invalid annotated XML file where the special characters are in their original form ```> , < , &```.

``` cat {formatted_input_filename} | DistFilter svr=xmlElem > {annotated_filename} ```

#### 3. Escape less than '<' character
Escape the less than characters that are followed by an alphabet or a period to its encoded form. We make use of Regular Expressions to handle this case since the XML Parsers do not handle this escaping.
The following exceptions are handled at this stage:
```
P<.001 --> P&lt;.001
P<or =0.004 --> P&lt;or =0.004
```



#### 4. Format output annotated file
Modify the annotated XML output into its valid XML format. This will result in a valid XML and escape the special characters as follows:

    < --> &lt;  
    > --> &gt: 
    & --> &amp; 

Our pipeline makes use of the BeautifulSoup4 XML parser to parse and replace the special characters back to their encoded form. 

#### Example

Let us take the term "HBB g.68A&gt;T" and see the corresponding notation in each of the stages of the pipeline. In the example below, we have chosen the annotation with the [Medical Subject Headings vocabulary](https://www.nlm.nih.gov/mesh/meshhome.html). 

+ In the dictionary -> Escaped 
--> ``` <t p1="" p2="" p3="">HBB g.68A&gt;T</t> ```

+ Input XML file-> Unescaped (using sed)
--> ``` HBB g.68A>T ```


+ After annotation -> Unescaped
--> ``` <z:mesh cui="" id="" semantics="">HBB g.68A>T</z:mesh > ```

+ Post annotation processing -> Escaped (using xml parser)
--> ``` <z:mesh cui="" id="" semantics="">HBB g.68A&gt;T</z:mesh > ```


You can find the code corresponding to the above pipeline in the [resources/monq folder](https://github.com/zbmed-semtec/whatizit-dictionary-ner/tree/main/resources/monq). The code at [main](https://github.com/zbmed-semtec/whatizit-dictionary-ner/blob/main/resources/monq/main.py) does the necessary pre-processing and post-processing of the files and results in the correct annotations. 

The code corresponding to the creation of a dictionary for the [Medical Subject Headings vocabulary](https://www.nlm.nih.gov/mesh/meshhome.html) is in the [code folder](https://github.com/zbmed-semtec/whatizit-dictionary-ner/tree/main/code). 

The documentation corresponding to the entire annotation process can be found in the [docs folder](https://github.com/zbmed-semtec/whatizit-dictionary-ner/blob/main/docs/annotate.md).