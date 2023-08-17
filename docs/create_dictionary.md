# Creating a dictionary

The **first** step to annotate text is creating the dictionary that will be used to identify expressions in the text and then associate them to a concept in a controlled vocabulary. For this, you need to select the vocabulary you want to support and then, for each preferred and alternative label, create an entry in the dictionary.

A dictionary looks like the XML file below. Notice that we have included some XML special characters (e.g., & < >) that might require some special treatment.
```
<?xml version='1.0' encoding='UTF-8'?>
<mwt xmlns:z="http://a.url/z">
<template><z:sample ids="%1">%0</z:sample></template>

<t p1="SAMPLE_1">cancer</t>
<t p1="SAMPLE_2">zyx</t>
<t p1="SAMPLE_3">AGPAT3</t>
<t p1="SAMPLE_3">1-acyl-sn-glycerol-3-phosphate acyltransferase gamma</t>
<t p1="SAMPLE_4">+ delta cadinene synthase isozyme C2</t>
<t p1="SAMPLE_5">cancer</t>
<t p1="SAMPLE_6">Parkinson's disease</t>
<t p1="SAMPLE_7">a reply to Smith &amp; Weist</t>
<t p1="SAMPLE_8">[Autopsies</t>
<t p1="SAMPLE_9">dead]</t>
<t p1="SAMPLE_10">protein-serine/threonine</t>
<t p1="SAMPLE_11">"AMBAR"</t>
<t p1="SAMPLE_12">p &lt; 0.001</t>
<t p1="SAMPLE_13">α-synuclein-containing</t>

<template>%0</template>
<r><z:[^>]*>(.*</z)!:[^>]*></r>
</mwt>
```
When parsing the dictionary and getting ready for annotation, whatizit/monq will add some regular expressions to it so the terms will be transformed as below.

| | | 
| :-: | :- | 
| ![!](./images/exclamation_mark.png) | The result will be the same regardless you use & or \&amp; in the dictionary (same for -- \&lt; and < -- or -- \&gt; and > --). The difference is that using \&amp; will result in a valid XML while using & will not (as it is a special character in XML so better to use the corresponding encoding). |
| | |

```
[Cc]ancers?[^A-Za-z0-9]
[Zz]yxs?[^A-Za-z0-9]
AGPAT3[^A-Za-z0-9]
1[ \-_]*[Aa]cyls?[ \-_]*[Ss]ns?[ \-_]*[Gg]lycerols?[ \-_]*3[ \-_]*[Pp]hosphates?[ \-_]*[Aa]cyltransferases?[ \-_]*[Gg]ammas?[^A-Za-z0-9]
\+[ \-_]*[Dd]eltas?[ \-_]*[Cc]adinenes?[ \-_]*[Ss]ynthases?[ \-_]*[Ii]sozymes?[ \-_]*C2[^A-Za-z0-9]
[Cc]ancers?[^A-Za-z0-9]
[Pp]arkinson's[ \-_]*[Dd]iseases?[^A-Za-z0-9]
a[ \-_]*[Rr]epl(y|ies)[ \-_]*to[ \-_]*[Ss]miths?[ \-_]*&[ \-_]*[Ww]eists?[^A-Za-z0-9]
\[Autopsies[^A-Za-z0-9]
[Dd]ead\][^A-Za-z0-9]
[Pp]roteins?[ \-_]*[Ss]erine/threonines?[^A-Za-z0-9]
"AMBAR"[^A-Za-z0-9]
p[ \-_]*<[ \-_]*0\.001[^A-Za-z0-9]
α[ \-_]*[Ss]ynucleins?[ \-_]*[Cc]ontainings?[^A-Za-z0-9]
```

| | | 
| :-: | :- | 
| ![Info](./images/information_mark.png) | As the special characters & < > will be recognized by the dictionary as such (and not as their encoded version \&amp; \&lt; \&gt;) the text to be annotated should also come with the non-encoded version of those characters.  |
| | If your text and dictionary terms use these characters, we suggest using, for instance, the ```sed``` linux command to replace the encoded version for the plain version ```sed 's/&lt;/</' sampleText.txt``` |
| | |

You can find the code corresponding to the creation of a dictionary for the [Medical Subject Headings vocabulary](https://www.nlm.nih.gov/mesh/meshhome.html) in the [code folder](../code). The code at [parse_csv](../code/create-dictionary/parse_csv.py) creates a dictionary of a CSV while [parser](../code/create-dictionary/parser.py) takes a turtle TTL file as input. Please be aware that due to license restrictions, we can only provide the code but not the actual data for the corresponding dictionary.

