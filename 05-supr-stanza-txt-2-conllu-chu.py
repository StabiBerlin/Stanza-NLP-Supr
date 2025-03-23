import stanza
import os
import time
import unicodedata
import sys
from datetime import datetime
from stanza.utils.conll import CoNLL
import re
from stanza.resources.common import list_available_languages

# only for stanza 1.9.0 and lower
#import torch
#original_torch_load = torch.load  # Original torch.load speichern
#def safe_torch_load(*args, **kwargs):
#    if "weights_only" not in kwargs:
#        kwargs["weights_only"] = False  # Standard auf False setzen
#    return original_torch_load(*args, **kwargs)
#torch.load = safe_torch_load  # Überschreibe torch.load

def remove_bracketed_words(text):
    """
    Removes all words (including brackets) that are enclosed in square brackets [].
    """
    return re.sub(r'\[.*?\]', '', text).strip()

 
def normalize_uppercase_words(text):
    """
    Converts fully uppercase words to lowercase for Stanza processing,
    while keeping a mapping with their positions (IDs) to restore them later.
    """
    words = text.split()

    def is_fully_upper(word):
        """ Prüft, ob das Wort nur aus Großbuchstaben besteht (ohne Satzzeichen). """
        clean_word = re.sub(r'[^\w]', '', word)  # Entfernt Satzzeichen
        return clean_word.isupper() and len(clean_word) > 2  # Mindestens 3 Zeichen lang

    # Speichere Großbuchstaben-Wörter mit Positionen
    word_map = {(word.lower(), idx + 1): word for idx, word in enumerate(words) if is_fully_upper(word)}
    
    #print("Word Map mit Positionen:", word_map)  # Debugging
    
    # Ersetze nur, wenn das Wort im Mapping existiert
    normalized_text = " ".join([word.lower() if (word.lower(), idx + 1) in word_map else word 
                                for idx, word in enumerate(words)])

    return normalized_text, word_map

def split_sentences(text):
    """
    Splits text into sentences using '.', ';' and ':' as delimiters,
    and ensures punctuation is treated as separate tokens.
    """
    # Ersetze "..." durch ein spezielles Zeichen, um es vor der Trennung zu schützen
    text = text.replace("...", " <ELLIPSIS> ")

    text = re.sub(r'([.;:,!?\"\'«»()\[\]{}„“·⁘])', r' \1 ', text)  # Separate punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    
    #return [s.strip() for s in re.split(r'(?<=[.;:])\s+', text) if s]

    # Jetzt nach Satzzeichen trennen, aber nicht nach "<ELLIPSIS>"
    sentences = [s.strip() for s in re.split(r'(?<=[.;:·⁘])\s+', text) if s]

    # Ersetze das Platzhalter-Zeichen wieder zurück in "..."
    sentences = [s.replace("<ELLIPSIS>", "...") for s in sentences]

    return sentences
    
def fix_punctuation(doc):
    """
    Ensures that punctuation is correctly tagged in the CoNLL-U format.
    - '&' and '...' are labeled as GAP.
    - '[]' and '()' are labeled as BRACKET.
    - Other punctuation is labeled as PUNCT.
    """
    punctuation_set = {'.', ',', ';', ':', '!', '?', '"', "'", '—','·','⁘'}
    gap_set = {'...'}  # Zeichen, die als GAP markiert werden
    bracket_set = {"[", "]", "(", ")", '{', '}', '«', '»', "„", "“"}  # Zeichen, die als BRACKET markiert werden

    for sentence in doc.sentences:
        for word in sentence.words:
            if word.text in punctuation_set:
                word.upos = "PUNCT"
                word.xpos = "PUNCT"
                word.lemma = "_"
                word.feats = "_"
                word.head = "0"
                word.deprel = "punct"
                word.deps = "0:punct"
                word.misc = "_"
            elif word.text in gap_set:  # "&" und "ß" als GAP markieren
                word.upos = "GAP"
                word.xpos = "GAP"
                word.lemma = "_"
                word.feats = "_"
                word.head = "0"
                word.deprel = "gap"
                word.deps = "0:gap"
                word.misc = "_"
            elif word.text in bracket_set:  # "[]" und "()" als BRACKET markieren
                word.upos = "BRACKET"
                word.xpos = "BRACKET"
                word.lemma = "_"
                word.feats = "_"
                word.head = "0"
                word.deprel = "bracket"
                word.deps = "0:bracket"
                word.misc = "_"

    return doc

def restore_original_casing(doc, word_map):
    """
    Restores the original uppercase words after Stanza processing, matching by ID.
    """
    for sentence in doc.sentences:
        for word in sentence.words:
            key = (word.text.lower(), word.id)  # ID & lowercased text als Schlüssel
            
            if key in word_map:
                #print(f"Restoring: {word.text} (ID {word.id}) -> {word_map[key]}")
                word.text = word_map[key]  # Originalwort wiederherstellen

    word_map.clear()  # Fix für Mischmasch
    return doc

def initialize_pipeline(language, processors, model_dir):
    """
    Initializes the Stanza pipeline with customized settings.
    """
    available_languages = list_available_languages()
    
    processor_list = ",".join(processors.keys())
    
    stanza.download(lang=language, processors=processor_list, model_dir=model_dir)
    
    pipeline = stanza.Pipeline(
        lang=language,
        processors=processors,
        use_gpu=False,
        model_dir=model_dir,
        tokenize_pretokenized=True,
        config={
            "tokenize_no_ssplit": True,
            "tokenize_punctuation": True
        }
    )
    
    # Extract actual processor configuration
    used_processors = pipeline.processors.keys()
    config_settings = pipeline.config
    
    # Remove model directory path from config settings
    short_config_settings = {
        key: value.replace(model_dir, "[MODEL_DIR]") if isinstance(value, str) else value
        for key, value in config_settings.items()
    }
    
    return pipeline, used_processors, short_config_settings

def process_text_file(nlp, used_processors, config_settings, input_path, conllu_path, language, processors, model_dir):
    """
    Processes a text file with the NLP pipeline and saves the results in CoNLL-U format.
    """
    with open(input_path, 'r', encoding='utf-8') as file:
        #text = file.read()
        lines = file.readlines()  # Lies Datei zeilenweise ein
    
    conllu_text = ""
    
    metadata = (
        f"# Language: {language}\n"
        f"# Processors: {processors}\n"
        f"# Used Processors: {used_processors}\n"
        f"# Config: {config_settings}\n"
        f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"# Stanza Version: {stanza.__version__}\n"
        f"# Python Version: {sys.version.split()[0]}\n"
    )
    conllu_text += metadata + "\n"

    for line in lines:
        line = line.strip()

        # Prüfen, ob die Zeile eine Segmentnummer enthält (z.B. [006])
        match = re.match(r"\[(\d+)\]", line)
        if match:
            segment_number = match.group(1)  # Extrahiere die Nummer
            line = line[match.end():].strip()  # Entferne die Segmentnummer aus der Zeile

    
        text = remove_bracketed_words(line)
        normalized_text, word_map = normalize_uppercase_words(text)  # Normalize uppercase before Stanza
        #print(normalized_text)
        sentences = split_sentences(normalized_text)
        
        for sentence in sentences:
            doc = nlp(sentence)    
            doc = restore_original_casing(doc, word_map)  # Restore uppercase words
            doc = fix_punctuation(doc)  # Fix punctuation first    
            
            if segment_number:
                conllu_text += f"# SN:{segment_number}\n"  # Füge Segmentnummer hinzu            
            
            for stanza_sentence in doc.sentences:
                for word in stanza_sentence.words:
                    conllu_text += (
                        f"{word.id}\t{word.text}\t{word.lemma}\t{word.upos}\t"
                        f"{word.xpos}\t{word.feats}\t{word.head}\t{word.deprel}\t"
                        f"{word.deps}\t{word.misc}\n"
                    )
                conllu_text += "\n"
    
    with open(conllu_path, 'w', encoding='utf-8') as file:
        file.write(conllu_text)

def process_directory(input_dir, output_dir, language, processors, model_dir):
    """
    Iterates through the directory and processes all text and CoNLL-U files.
    """
    nlp, used_processors, config_settings = initialize_pipeline(language, processors, model_dir)
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".txt"):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, input_dir)
                conllu_path = os.path.join(output_dir, "conllu", relative_path.replace(".txt", ".conllu"))
                
                os.makedirs(os.path.dirname(conllu_path), exist_ok=True)
                
                start_time = time.time()
                process_text_file(nlp, used_processors, config_settings, input_path, conllu_path, language, processors, model_dir)
                end_time = time.time()
                print(f"File '{input_path}' processed in {end_time - start_time:.2f} seconds.")

# Main execution
if __name__ == "__main__":
    input_directory = "./target"
    output_directory = "./out-chu-" + stanza.__version__
    language = "cu"
    model_directory = "./stanza_resources-" + stanza.__version__

    processors = {
        "tokenize": "default",
        "pos": "default",
        "lemma": "default",
        "depparse": "default"
    }

    start_time_all = time.time()
    
    process_directory(input_directory, output_directory, language, processors, model_directory)
    
    end_time_all = time.time()
    
    print(f"Files processed in {start_time_all - end_time_all:.2f} seconds.")
