import os
import argparse
from bs4 import BeautifulSoup
import warnings


def format_input(input_path, formatted_input_path):
    """Formats the input XML files by unescaping the escaped special characters.
    Replaces the HTML encoding of the special characters to its original form.
    The conversion is as follows:
    &lt; --> <
    &gt: --> >
    &amp; --> &
    Input:  input_path -> str: Filepath of the input XML file.
            formatted_input_path -> str: Filepath for the formatted XML file.
    """
    for file in os.listdir(input_path):
        input= os.path.join(input_path, file)
        filename = file.split('.')[0] + '_sed.' + file.split('.')[1]
        output = os.path.join(formatted_input_path, filename)
        os.system(f"sed 's/&lt;/</g;s/&gt;/>/g;s/&amp;/\&/g' {input} > {output}")
    os.system("echo $(date) Formatted input files")

def annotate(formatted_input_path, output_path):
    """Annotates the formatted input XML files with the MESH dictionary using the whatizit tool.
    Input: formatted_input_path -> str: Filepath of the formatted XML file.
           output_path-> str: Filepath for the annotated XML file.
    """
    counter = 0
    for file in os.listdir(formatted_input_path):
        counter += 1
        input = os.path.join(formatted_input_path, file)
        filename = file.split('_')[0] + '_temp_annotated.xml'
        output = os.path.join(output_path, filename)
        os.system(f"cat {input} | DistFilter svr=xmlElem > {output}")
        os.system(f"echo $(date) {filename} {counter}")   
    os.system("echo Annotation completed")

def format_output(output_path, formatted_output_path):
    """Formats the annotated XML output into its valid XML format.
    Input: output_path -> str: Filepath of the annotated XML file.
           formatted_output_path -> str: Filepath for the nanformatted annotated XML file.
    """
    for file in os.listdir(output_path):
        temp_output = os.path.join(output_path, file)
        with open(temp_output, "r") as file_data:
            # Read each line in the file, readlines() returns a list of lines
            contents = file_data.readlines()
            first_line = contents[0]
            # Adding namespace
            contents[1] = contents[1].split(">")[0] + ' xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner">\n'
            # Combine the lines in the list into a string
            contents = "".join(contents)
            soup = BeautifulSoup(contents, "lxml")
        filename = file.split('_')[0] + '_annotated.xml'
        output = os.path.join(formatted_output_path, filename)
        f = open(output, "w")
        f.write(first_line)
        f.write(str(soup.body.next))
        f.close()
    os.system(f"echo $(date) Formatted annotated files")   


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="Name of the dataset to be annotated (TREC/RELISH)")
    args = parser.parse_args()
    dataset = args.dataset
    dir = os.getcwd()
    input_path = os.path.join(dir, f'text/{dataset}/input')
    formatted_input_path = f'{dir}/text/{dataset}/formatted_input'
    output_path = f'{dir}/output/{dataset}/annotations'
    formatted_output_path = f'{dir}/output/{dataset}/formatted_output'
    if not os.path.exists(formatted_input_path):
        os.makedirs(formatted_input_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(formatted_output_path):
        os.makedirs(formatted_output_path)
    format_input(input_path, formatted_input_path)
    annotate(formatted_input_path, output_path)
    format_output(output_path, formatted_output_path)