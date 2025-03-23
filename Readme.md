# Stanza-NLP-Supr

**Effective Use of NLP Methods: A Case Study on the Codex Suprasliensis**

This repository contains all scripts, data transformation steps, evaluation tools, and results associated with a linguistic and computational analysis of the _Codex Suprasliensis_. The project demonstrates how NLP technologies, in particular [Stanza](https://stanfordnlp.github.io/stanza/), can be effectively applied to pre-modern texts in multiple languages (Old Church Slavonic and Ancient Greek).

---

## Overview

The workflow consists of the following major stages:

### 1. Data Extraction and Cleaning

- **`01-supr-import-data.py`**
  - Extracts aligned parallel text from HTML files from `suprasliensis.obdurodon.org`
  - Normalizes special characters, removes `<span>` tags, and flattens structure
  - Output: `supr_extracted_data.tsv`

### 2. Text Segmentation and Alignment

- **`02-supr-parsen-001.py`**
  - Merges fragmented rows based on punctuation, adds numbered segment IDs (e.g., `<001r1>`)
  - Produces structured TSV and HTML view
  - Output: `supr_df_merged.tsv`, `supr_df_merged.html`

### 3. Thematic Label Assignment

- **`03-supr_labeln-001.py`**
  - Assigns thematic labels to each segment based on an external file (`folios_new_proofed.txt`)
  - Output: `supr_df_labeled.tsv`, `supr_df_labeled.html`

### 4. Corpus Export

- **`04-supr-df-2-txt.py`** & **`04-01-supr-df-2-txt-grc.py`**
  - Export the Old Church Slavonic and Ancient Greek segments into line-numbered plain text files for NLP processing
  - Output: `target/supr_all_segments.txt`, `target-grc/supr_all_segments.txt`

### 5. NLP Processing with Stanza

- **`05-supr-stanza-txt-2-conllu-chu.py`**
  - Applies a custom Stanza pipeline for Old Church Slavonic using manually downloaded models

- **`05-01-supr-stanza-txt-2-conllu-gre.py`**
  - Processes Ancient Greek using the `proiel_nocharlm` models

  - Outputs: CoNLL-U files in `./out-chu-*` and `./out-grc-*`

### 6. Feature Enrichment

- **`06-supr-df-enlarge-001.py`**
  - Adds POS and Lemma annotations to each row in `supr_df_labeled.tsv` by aligning them with the CoNLL-U output
  - Output: `supr_df_enlarged.tsv`, `supr_df_enlarged.html`

### 7. Linguistic Visualization

- **`07-supr-adj-visual-001.py`**
  - Generates charts showing the distribution of POS tags (especially ADJ and VERB) per thematic label

### 8. Text Clustering

- **`08-supr-clustern-001.py`**
  - Applies t-SNE dimensionality reduction and KMeans clustering on TF-IDF trigram vectors of lemmas
  - Output: `clustered_labels_with_similarity.tsv`, `tsne_clustering.png`

### 9. Corpus Export for AntConc

- **`09-supr-conllu-2-antconc.py`**
  - Converts CoNLL-U files into a format suitable for corpus analysis with AntConc, grouped by thematic label

---

## Evaluation Tools

### CoNLL-U Format Scoring

- **`conll18_ud_eval.py`**
  - Official Universal Dependencies evaluation script (CoNLL 2018)
  - Can be used manually or via the wrapper below

- **`stanza-eval-versions.py`**
  - Downloads the latest evaluation script if not present
  - Compares different Stanza output versions (e.g., 1.10.1 vs. 1.9.0)
  - Outputs: `evaluation_results.txt`

---

## Results Presentation

Three key HTML files provide insight into the corpus and annotation pipeline:

- **`supr_df_merged.html`**: merged and normalized parallel segments (Slavonic + Greek)
- **`supr_df_labeled.html`**: same, with thematic labels
- **`supr_df_enlarged.html`**: extended with POS tags and lemmata

---

## Project Output: Scientific Article

This code base and its associated results form the empirical basis for the article:

> **"Effektiver Einsatz von NLP-Methoden am Beispiel des Codex Suprasliensis"**

The article discusses methodological challenges, NLP evaluation metrics, and linguistic phenomena revealed by the cross-linguistic comparison of the Codex.

---

## Dependencies

- Python ≥ 3.8
- Stanza ≥ 1.4.0 (manual model downloads for Old Church Slavonic may be required)
- pandas, matplotlib, seaborn, scikit-learn, BeautifulSoup4
- t-SNE & KMeans (via `sklearn.manifold` and `sklearn.cluster`)

---

## License

- All Python scripts and original analysis code in this repository are released under the **MIT License**.  
- Input texts: Derived from `suprasliensis.obdurodon.org` (maintained by David J. Birnbaum)

These texts are licensed under the  
**Creative Commons BY-NC-SA 3.0 Unported License**  
(Attribution – NonCommercial – ShareAlike).


---

## Author

This project was designed for historical-linguistic analysis using modern NLP pipelines, showcasing both linguistic insight and computational processing strategies.

