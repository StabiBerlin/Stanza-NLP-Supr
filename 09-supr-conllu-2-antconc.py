import os
import pandas as pd
import unicodedata
from stanza.utils.conll import CoNLL

def replace_special_chars(text: str) -> str:
    replacements = {"ѣ": "е", "ꙙ": "я", "ѧ": "я", "ꙗ": "я", "ꙑ": "ы", "ꙋ": "у", "ꙁ": "з", "ѫ": "ю", "ѥ": "ие"}
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    return text.lower()

def remove_polytonic_chars(text: str) -> str:
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in normalized_text if not unicodedata.combining(c) and c not in "῾᾿")

def extract_segments_from_conllu(conllu_path):
    """
    Extracts segments from a single CoNLL-U file and returns a dictionary mapping segment numbers to their content.
    """
    with open(conllu_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    segments = {}
    current_segment = []
    current_segment_numbers = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("# SN:"):
            if current_segment_numbers:
                for seg_num in current_segment_numbers:
                    segments.setdefault(seg_num, []).extend(current_segment)
            
            current_segment_numbers = [int(num) for num in line.split(":")[1].split()]
            current_segment = [line]
        else:
            current_segment.append(line)
    
    if current_segment_numbers:
        for seg_num in current_segment_numbers:
            segments.setdefault(seg_num, []).extend(current_segment)
    
    return segments

def convert_conllu_to_pos(segment_lines):
    """
    Converts a segment's lines to the POS format.
    """
    pos_text = ""
    sentence = []
    
    for line in segment_lines:
        line = line.strip()
        if line.startswith("# SN:"):
            segment_numbers = line.split(":")[1]
            pos_text += "[" + segment_numbers + "] "
            continue
        
        if line and not line.startswith("#"):
            columns = line.split("\t")
            if len(columns) > 3:
                word_text = columns[1]
                lemma = columns[2]
                upos = columns[3]
                feats = columns[5]
                
                nword = replace_special_chars(word_text)
                nword = remove_polytonic_chars(nword)
                
                if upos == "PUNCT":
                    sentence.append(f"{word_text}")
                else:
                    sentence.append(f" {word_text}_{upos}|l={lemma}|n={nword}|{feats}")
        else:
            if sentence:
                pos_text += "".join(sentence) + " "  # Zusammenführung mit Leerzeichen
                sentence = []
    
    return pos_text.strip()

def process_conllu_by_label(conllu_path, tsv_path, output_dir):
    df = pd.read_csv(tsv_path, sep="\t")
    segments = extract_segments_from_conllu(conllu_path)
    
    grouped_segments = {}
    for index, row in df.iterrows():
        label = row['Label']
        segment_number = index  # Assuming index corresponds to segment number
        
        if segment_number in segments:
            if label not in grouped_segments:
                grouped_segments[label] = []
            grouped_segments[label].extend(segments[segment_number])
    
    for label, segment_lines in grouped_segments.items():
        label_dir = os.path.join(output_dir, str(label))
        os.makedirs(label_dir, exist_ok=True)
        pos_text = convert_conllu_to_pos(segment_lines)
        
        pos_path = os.path.join(label_dir, f"label_{label}.txt")
        with open(pos_path, 'w', encoding='utf-8') as file:
            file.write(pos_text)
        print(f"Saved: {pos_path}")

# Main execution
if __name__ == "__main__":
    input_conllu_file = "./out-chu-1.10.1/conllu/supr_all_segments.conllu"  # Gesamtdatei mit allen Segmenten
    tsv_path = "./supr_df_labeled.tsv"  # TSV-Datei mit Labels
    output_directory = "./out-chu-1.10.1/pos-antconc"
    
    os.makedirs(output_directory, exist_ok=True)
    process_conllu_by_label(input_conllu_file, tsv_path, output_directory)
