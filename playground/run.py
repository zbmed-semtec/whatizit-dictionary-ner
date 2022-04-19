import os
from lxml import etree 


# dir = os.getcwd()
# subdir = os.path.join(dir, "text/test")
# for file in os.listdir(subdir):
#     filename = os.path.join(subdir, file)
#     os.system(f"echo {filename}")
#     os.system(f"sed 's/&lt;/</g;s/&gt;/>/g;s/&amp;/&/g' {filename} > {filename}")


parser = etree.XMLParser(recover=True)
tree = etree.parse("./text/test/dummy.xml", parser)
root = tree.getroot()
with open('dummy_output.xml', 'wb') as f:
    tree.write(f, encoding='utf-8', xml_declaration=True)
