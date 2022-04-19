import os
from lxml import etree 
from bs4 import BeautifulSoup


# dir = os.getcwd()
# subdir = os.path.join(dir, "text/test")
# for file in os.listdir(subdir):
#     filename = os.path.join(subdir, file)
#     os.system(f"echo {filename}")
#     os.system(f"sed 's/&lt;/</g;s/&gt;/>/g;s/&amp;/&/g' {filename} > {filename}")


# parser = etree.XMLParser(recover=True)
# tree = etree.parse("workbook.xml", parser)
# root = tree.getroot()

# with open('dummy_output.xml', 'wb') as f:
#     tree.write(f, encoding='utf-8', xml_declaration=True)



with open("dummy.xml", "r") as file:
    # Read each line in the file, readlines() returns a list of lines
    contents = file.readlines()
    first_line = contents[0]
    # Combine the lines in the list into a string
    contents = "".join(contents)
    soup = BeautifulSoup(contents, "lxml")

f = open("dummy_output.xml", "w")
f.write(first_line)
f.write(str(soup.body.next))
f.close()