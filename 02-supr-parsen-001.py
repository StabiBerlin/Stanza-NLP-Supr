import re
import pandas as pd
import matplotlib.pyplot as plt

# Datei einlesen
file_path = 'supr_extracted_data.tsv'
df = pd.read_csv(file_path, sep='\t')

# Funktion zum Mergen der Zellen im Griechischen Text, wenn kein Punkt "·" am Ende vorkommt
def merge_rows_without_dot(df):
    merged_data = []
    temp_row = df.iloc[0].copy()

    for index in range(1, len(df)):
        row = df.iloc[index]
        os_content_temp = str(temp_row['OS Content'])
        #if not os_content_temp.strip().endswith('·'):
        if not os_content_temp.strip().endswith(('·', '⁘')):
            # Check for hyphen at the end and remove it if present
            if os_content_temp.strip().endswith('-'):
                temp_row['H3 Content'] = str(temp_row['H3 Content']).rstrip('-') + str(row['H3 Content'])
                temp_row['OS Content'] = os_content_temp.rstrip('-') + str(row['OS Content'])
                temp_row['GK Content'] = str(temp_row['GK Content']).rstrip('-') + str(row['GK Content'])
            else:
                temp_row['H3 Content'] = str(temp_row['H3 Content']) + " " + str(row['H3 Content'])
                temp_row['OS Content'] += " " + str(row['OS Content'])
                temp_row['GK Content'] = str(temp_row['GK Content']) + " " + str(row['GK Content'])
        else:
            merged_data.append(temp_row)
            temp_row = row.copy()
    
    # Hinzufügen des letzten Eintrags
    merged_data.append(temp_row)
    
    return pd.DataFrame(merged_data)


def merge_gk_content_with_comma(df):
    """
    Funktion zur Zusammenführung von Zeilen, falls `GK Content` mit `,` endet.
    Die Zeilen werden nur zusammengeführt, wenn `GK Content` mit `,` endet.
    """
    merged_data = []  # Liste für das neue DataFrame
    temp_row = df.iloc[0].copy()  # Erste Zeile als Startpunkt
    
    for index in range(1, len(df)):
        row = df.iloc[index]
        
        # Prüfen, ob `GK Content` mit `,` endet
        if str(temp_row['GK Content']).strip().endswith(','):
            # Falls ja, Zeilen zusammenführen
            temp_row['H3 Content'] += " " + row['H3 Content']
            temp_row['OS Content'] += " " + row['OS Content']
            temp_row['GK Content'] += " " + row['GK Content']
        else:
            # Falls nein, speichere die zusammengeführte Zeile und starte neu
            merged_data.append(temp_row.copy())
            temp_row = row.copy()
    
    # Letzte Zeile hinzufügen
    merged_data.append(temp_row)

    # Erstelle ein neues DataFrame mit neuem Index
    df_merged = pd.DataFrame(merged_data).reset_index(drop=True)

    return df_merged

def merge_rows_without_dot_with_num(df):
    merged_data = []
    temp_row = df.iloc[0].copy()
    current_id = temp_row['H3 Content'][:5]  # Extrahiere die ID im Format <001r>, <001v>, etc.
    counter = 1  # Initialisiere den Zähler für die Nummerierung
    
    # Füge Nummerierung zum ersten Eintrag hinzu
    temp_row['H3 Content'] = current_id + str(counter) + '>'
    
    for index in range(1, len(df)):
        row = df.iloc[index]
        os_content_temp = str(temp_row['OS Content'])
        gk_content_temp = str(temp_row['GK Content'])
        new_id = row['H3 Content'][:5]  # Extrahiere die ID für die aktuelle Zeile
        
        if new_id == current_id:
            counter += 1  # Erhöhe den Zähler für die gleiche ID
        else:
            current_id = new_id
            counter = 1  # Zurücksetzen des Zählers bei ID-Wechsel
        
        # Erweitere `H3 Content` um die aktuelle Nummer für die aktuelle Zeile
        df.loc[index, 'H3 Content'] = new_id + str(counter) + '>'

        #print(f"Zeile {index}: OS Content vorher: '{os_content_temp}'")
        #print(f"Zeile {index}: GK Content vorher: '{gk_content_temp}'")

        # or not gk_content_temp.strip().endswith('·')
        if not os_content_temp.strip().endswith(('·', '⁘')) or gk_content_temp.strip().endswith(('Εὐνόϊ-','αἰ-','διαπο-','ἐτυπή-','ἀπιστο-')) or len( temp_row['OS Content'].strip().split()) <= 20:
            if os_content_temp.strip().endswith('-'):
                temp_row['H3 Content'] = str(temp_row['H3 Content']).rstrip('-') + row['H3 Content']
                temp_row['OS Content'] = os_content_temp.rstrip('-') + str(row['OS Content'])
                temp_row['GK Content'] = str(temp_row['GK Content']).rstrip('-') + str(row['GK Content'])
            else:
                temp_row['H3 Content'] = str(temp_row['H3 Content']) + " " + row['H3 Content']
                temp_row['OS Content'] += " " + str(row['OS Content'])
                temp_row['GK Content'] = str(temp_row['GK Content']) + " " + str(row['GK Content'])
            
            # Debugging: Ausgabe von `OS Content` nach der Änderung
            #print(f"Zeile {index}: OS Content nachher: '{temp_row['OS Content']}'")
        
        else:
            merged_data.append(temp_row)
            temp_row = row.copy()

        temp_row['H3 Content'] = re.sub(r'\s+', '', temp_row['H3 Content'])  # Hier nochmal bereinigen!
        temp_row['GK Content'] = re.sub(r'- ', '', temp_row['GK Content'])
        
    # Hinzufügen des letzten Eintrags
    merged_data.append(temp_row)
    
    return pd.DataFrame(merged_data)

# Sicherstellen, dass keine NaN-Werte in den relevanten Spalten vorhanden sind, um Fehler zu vermeiden
df.loc[:, 'OS Content'] = df['OS Content'].fillna("")
df.loc[:, 'H3 Content'] = df['H3 Content'].fillna("")
df.loc[:, 'GK Content'] = df['GK Content'].fillna("")

# Anwenden der Funktion auf das DataFrame
#df_merged = merge_rows_without_dot(df)

#df = df.head(300)
df_merged = merge_rows_without_dot_with_num(df)
df_merged = merge_gk_content_with_comma(df_merged)

# Anzeigen der ersten Zeilen des aktualisierten DataFrames
df_merged.head()


# Konvertieren des DataFrames in eine HTML-Tabelle mit Bootstrap-Klassen
html_table = df_merged.reset_index().to_html(classes='table table-striped table-bordered', index=False)

# HTML-Seite mit Bootstrap einbetten
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
            th:first-child, td:first-child {{ width: 10%; word-wrap: break-word; overflow-wrap: break-word; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 class="my-4">DataFrame "Codex Suprasliensis" merged (from suprasliensis.obdurodon.org)</h2>
            {html_table}
        </div>
    </body>
    </html>
"""

# Speichern der HTML-Seite in einer Datei
with open('supr_df_merged.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

tsv_path = 'supr_df_merged.tsv'
with open(tsv_path, 'w', encoding='utf-8') as tsv_file:
    tsv_file.write("H3 Content\tOS Content\tGK Content\n")  # Header
    for _, row in df_merged.iterrows():
        tsv_file.write(f"{row['H3 Content']}\t{row['OS Content']}\t{row['GK Content']}\n")

