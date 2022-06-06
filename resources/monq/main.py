import os
import re
import argparse
from bs4 import BeautifulSoup
import warnings
import logging


logging.basicConfig(filename='../monq/logging/annotation.log', filemode='w',
                    level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def format_input(input_path, formatted_input_path) -> None:
    """Formats the input XML files by unescaping the escaped special characters.
    Replaces the HTML encoding of the special characters to its original form.
    The conversion is as follows:
    &lt; --> <
    &gt: --> >
    &amp; --> &
    
    Parameters
    ----------
    input_path : str
        Filepath of the input XML file.
    formatted_input_path : str
        Filepath for the formatted XML file.
    """
    logging.info("Starting annotation of {} XML files".format(dataset.upper()))
    for file in os.listdir(input_path):
        if not file.endswith(".DS_Store"):
            input = os.path.join(input_path, file)
            filename = file.split('.')[0] + '_sed.' + file.split('.')[1]
            output = os.path.join(formatted_input_path, filename)
            os.system(f"sed 's/&lt;/</g;s/&gt;/>/g;s/&amp;/\&/g' {input} > {output}")
    logging.info("Formatted input files")


def annotate(formatted_input_path, output_path, n_files) -> None:
    """Annotates the formatted input XML files with the MESH dictionary using the whatizit tool.
    
    Parameters
    ----------
    formatted_input_path : str
        Filepath of the formatted XML file.
    output_path : str
        Filepath for the annotated XML file.
    n_files : int
        Number of files to annotate.
    """
    files = [file for file in sorted(os.listdir(formatted_input_path)) if not file.endswith('.DS_Store')][:n_files]
    batches = [files[i:i+1000] for i in range(0, len(files), 1000)]
    counter = 1
    for batch in batches:
        start = batch[0]
        end = batch[-1]
        for file in batch:
            input = os.path.join(formatted_input_path, file)
            filename = file.split('_')[0] + '_temp_annotated.xml'
            output = os.path.join(output_path, filename)
            os.system(f"cat {input} | DistFilter svr=xmlElem > {output}")
        logging.info("Annotatted files of batch {}. Start : {} End: {} ".format(counter, start, end))
        counter += 1


def escape_character(contents) -> str:
    """
    Converts the '<' character to its encoded form.
    Replaces the '<' character if it is followed by alphabets or a period other than those 
    in the annotation tags to &lt;.
    
    Parameters
    ----------
    contents : str
        Body of the annotated XML file.
    Returns
    ----------
    contents : str
        Formatted body of the annotated XML file.
    """
    texts = re.findall(r'<text>(.*?)</text>', contents, re.DOTALL)
    title = texts[0]
    abstract = texts[1]
    contents = contents.replace(title, re.sub(r"<(?!(/*)z:MESH)", "&lt;", title))
    contents = contents.replace(abstract, re.sub(r"<(?!(/*)z:MESH)", "&lt;", abstract))
    return contents


def format_output(output_path, formatted_output_path) -> None:
    """Formats the annotated XML output into its valid XML format.
    
    Parameters
    ----------
    output_path : str
        Filepath of the annotated XML file.
    formatted_output_path : str
        Filepath for the nanformatted annotated XML file.
    """
    for file in os.listdir(output_path):
        temp_output = os.path.join(output_path, file)
        with open(temp_output, "r") as file_data:
            # Read each line in the file, readlines() returns a list of lines
            contents = file_data.readlines()
            first_line = contents[0]
            # Adding namespace
            contents[1] = contents[1].split(">")[0] + ' xmlns:z="https://github.com/zbmed-semtec/whatizit-dictionary-ner#">\n'
            # Combine the lines in the list into a string
            contents = "".join(contents)
            formatted_contents = escape_character(contents)
            soup = BeautifulSoup(formatted_contents, "lxml")
        filename = file.split('_')[0] + '_annotated.xml'
        output = os.path.join(formatted_output_path, filename)
        f = open(output, "w")
        f.write(first_line)
        f.write(str(soup.body.next))
        f.close()
    logging.info("Formatted {} annotated files".format(n_files))   


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="Name of the dataset to be annotated (TREC/RELISH)")
    parser.add_argument("--n", type=int, help="Number of files to be annotated")
    args = parser.parse_args()
    dataset = args.dataset
    n_files = args.n
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
    annotate(formatted_input_path, output_path, n_files)
    format_output(output_path, formatted_output_path)