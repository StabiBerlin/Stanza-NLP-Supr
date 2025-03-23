import pandas as pd
import re

# Funktion zum Laden der Daten
def load_data(df_path, labels_path):
    df = pd.read_csv(df_path, sep='\t', dtype=str)
    labels_df = pd.read_csv(labels_path, sep='\t', names=["Position", "Label"], dtype=str)
    return df, labels_df

# Funktion zur Zuweisung der Labels basierend auf 'H3 Content'
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

# Funktion zum Speichern als HTML
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
            <h2 class="my-4">DataFrame "Codex Suprasliensis" labeled (from suprasliensis.obdurodon.org)</h2>
            {html_table}
        </div>
    </body>
    </html>
    """
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML-Datei gespeichert: {output_html_path}")

# Hauptfunktion
def main(df_path, labels_path, output_path, output_html_path):
    df, labels_df = load_data(df_path, labels_path)
    df = assign_labels(df, labels_df, h3_column='H3 Content')
    df.fillna('', inplace=True)
    df.to_csv(output_path, sep='\t', index=False)
    save_as_html(df, output_html_path)
    print(f"Verarbeitung abgeschlossen. Dateien gespeichert unter: {output_path} und {output_html_path}")

if __name__ == "__main__":
    dataframe_path = 'supr_df_merged.tsv'
    labels_path = 'folios_new_proofed.txt'
    output_path = 'supr_df_labeled.tsv'
    output_html_path = 'supr_df_labeled.html'
    main(dataframe_path, labels_path, output_path, output_html_path)