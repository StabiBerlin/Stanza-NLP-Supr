import os
import pandas as pd
from bs4 import BeautifulSoup
import re

# Define a function to normalize the text
def normalize_text(text):
    text = text.replace(' 001r ', '001r')  # special case
    text = text.replace('\xa0', '')  # Remove the specific character
    text = text.replace('ꙿ', '꙽')  # Replace A67F CYRILLIC PAYEROK > A67D COMBINING CYRILLIC PAYEROK
    #text = re.sub(r'<br\/>', '\n', text)
    text = re.sub(r'\n\s+', '', text)
    text = text.strip()  # Remove leading and trailing spaces
    return text

def remove_deleted_spans_with_regex(text):
    # Regular expression to match and remove the <span class="deleted">...</span> while preserving spaces
    pattern = re.compile(r'<span class="deleted">.*?</span>')
    # Substitute the matched pattern with a single space
    modified_text = pattern.sub('', text)
    return modified_text

# Define a function to replace <span class="add">...</span> with the content inside the span
def replace_add_spans(text):
    # Regular expression to match <span class="add">...</span>
    pattern = re.compile(r'<span class="add">(.*?)</span>')
    # Substitute the matched pattern with the content inside the span
    #modified_text = pattern.sub(r'\1', text)
    modified_text = pattern.sub(r'', text)
    return modified_text

def del_spaces(text):
    text = re.sub(r'\n\s+', '', text)    
    text = re.sub(r'\s+', ' ', text)
    # Delete spaces between chars
    text = re.sub(r'(?<=[^\W\d_])-(?=[^\W\d_])', '', text, flags=re.UNICODE)
    text = re.sub(r'-ж', ' ж', text, flags=re.UNICODE)    
    text = re.sub(r'(и҅)-(?=[^\W\d_])', '', text, flags=re.UNICODE) # Special case
    text = re.sub(r'(ѥ҅)-(?=[^\W\d_])', '', text, flags=re.UNICODE) # Special case

    

    return text
    
# Define a function to extract data from a single HTML file
def extract_data_from_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        file_content = remove_deleted_spans_with_regex(file_content)
        file_content = replace_add_spans(file_content)
        file_content = del_spaces(file_content)
    soup = BeautifulSoup(file_content, 'html.parser')
    

    
    data = []
    for li in soup.find_all('li'):
        h3_content = normalize_text(soup.find('h3').get_text(strip=True))
        os_content = normalize_text(li.find('span', class_='os').get_text(strip=True)) if li.find('span', class_='os') else ''
        gk_content = normalize_text(li.find('span', class_='gk').get_text(strip=True)) if li.find('span', class_='gk') else ''
        data.append(f"{h3_content}\t{os_content}\t{gk_content}")
    return data

# Process all HTML files in a directory
def process_directory(directory):
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            data = extract_data_from_html_file(file_path)
            all_data.extend(data)
    return all_data

# Specify the directory containing the HTML files
directory_path = './suprasliensis.obdurodon.org/pages'  # Ersetzen Sie dies durch den Pfad zum Verzeichnis mit den HTML-Dateien

# Extract data from all files in the directory
all_data = process_directory(directory_path)

# Save the extracted data to a TSV file
tsv_path = 'supr_extracted_data.tsv'
with open(tsv_path, 'w', encoding='utf-8') as tsv_file:
    tsv_file.write("H3 Content\tOS Content\tGK Content\n")  # Write the header
    tsv_file.write("\n".join(all_data))  # Write the data

print('Data has been extracted and saved to supr_extracted_data.tsv')
