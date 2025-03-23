import pandas as pd
import re

def load_data(df_path, labels_path):
    df = pd.read_csv(df_path, sep='\t', dtype=str)
    labels_df = pd.read_csv(labels_path, sep='\t', names=["Position", "Label"], dtype=str)
    return df, labels_df

def assign_labels(df, labels_df, h3_column='H3 Content'):
    label_dict = dict(zip(labels_df["Position"], labels_df["Label"]))
    labels = []
    
    for pos_group in df[h3_column]:
        positions = re.findall(r'<[^>]+>', pos_group)
        assigned_label = None
        
        for pos in positions:
            label = label_dict.get(pos, '').strip()
            if label.lower() != 'leer' and label:
                assigned_label = label
                break
        
        labels.append(assigned_label)
    
    df['Label'] = labels
    return df

def extract_data_from_conllu(conllu_path):
    lemma_dict = {}
    pos_dict = {}
    current_sn = None  # Speichert die aktuelle SN-Nummer
    
    with open(conllu_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('# SN:'):
                current_sn = re.sub(r'[^0-9]', '', line.split(':')[1])  # Nur Zahlen extrahieren
                if current_sn:
                    current_sn = int(current_sn)  # In Integer umwandeln
                    if current_sn not in lemma_dict:
                        lemma_dict[current_sn] = []
                        pos_dict[current_sn] = []
            elif current_sn is not None and line and not line.startswith('#'):
                columns = line.split('\t')
                if len(columns) > 4:
                    lemma_dict[current_sn].append(columns[2] if columns[2] != 'None' else '.')
                    pos_dict[current_sn].append(columns[3] if columns[3] != 'None' else '.')
    
    print("Extrahierte SNs aus CoNLL-U:", sorted(list(lemma_dict.keys()))[:10])  # Debugging-Ausgabe
    return {sn: ' '.join(lemmas) for sn, lemmas in lemma_dict.items()}, {sn: ' '.join(pos) for sn, pos in pos_dict.items()}

def merge_with_conllu_data(df, lemma_dict, pos_dict):
    # Verwenden der Lfd-Nr. als SN-Referenz, normalisiert auf Zahlen
    df['SN'] = df.index + 1  # Lfd-Nr. beginnt bei 1
    df['Lemmata'] = df['SN'].map(lemma_dict).fillna('.')  # Ersetze leere Werte mit '.'
    df['POS'] = df['SN'].map(pos_dict).fillna('.')  # Wortarten hinzufügen
    print("Erste 10 Lfd-Nr. Werte:", df['SN'].head(10).tolist())  # Debugging-Ausgabe
    return df.drop(columns=['SN'])

def save_as_html(df, output_html_path):
    df.insert(0, 'Lfd-Nr.', range(1, len(df) + 1))
    html_table = df.to_html(classes='table table-striped table-bordered', index=False)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <link href="css/style.css" rel="stylesheet" type="text/css">        
        <title>DataFrame Table</title>
        <style>
            table {{ width: 100%; table-layout: fixed; }}
            th, td {{ word-wrap: break-word; overflow-wrap: break-word; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 class="my-4">DataFrame mit Labels und Lemmata</h2>
            {html_table}
        </div>
    </body>
    </html>
    """
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML-Datei gespeichert: {output_html_path}")

def main(df_path, labels_path, conllu_path, output_path, output_html_path):
    df, labels_df = load_data(df_path, labels_path)
    df = assign_labels(df, labels_df, h3_column='H3 Content')
    lemma_dict, pos_dict = extract_data_from_conllu(conllu_path)
    df = merge_with_conllu_data(df, lemma_dict, pos_dict)
    df.fillna('.', inplace=True)  # Ersetze alle NaN-Werte mit '.'
    df.to_csv(output_path, sep='\t', index=False)
    save_as_html(df, output_html_path)
    print(f"Verarbeitung abgeschlossen. Dateien gespeichert unter: {output_path} und {output_html_path}")

if __name__ == "__main__":
    dataframe_path = 'supr_df_merged.tsv'
    labels_path = 'folios_new_proofed.txt'
    conllu_path = './out-chu-1.10.1/conllu/supr_all_segments.conllu'
    output_path = 'supr_df_enlarged.tsv'
    output_html_path = 'supr_df_enlarged.html'
    main(dataframe_path, labels_path, conllu_path, output_path, output_html_path)