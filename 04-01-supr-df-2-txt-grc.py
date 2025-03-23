import os
import pandas as pd

# DataFrame laden
df = pd.read_csv("supr_df_labeled.tsv", sep="\t")  # Falls TSV

# NaN-Werte in der Spalte "GK Content" durch leere Strings ersetzen
df["GK Content"] = df["GK Content"].fillna("")

# Datei für die gesamte Ausgabe
output_file = "./target-grc/supr_all_segments.txt"

# Sicherstellen, dass das Verzeichnis existiert
os.makedirs("target-grc", exist_ok=True)

# Texte sammeln und mit [001], [002], ... nummerieren
texts = []
for idx, content in enumerate(df["GK Content"], start=1):
    texts.append(f"[{idx:04d}] {content}")  # Format: [001] Text

# Gesamttext speichern
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n\n".join(texts))  # Jeder Eintrag durch zwei Zeilenumbrüche getrennt

print(f"Die gesamte OS Content-Spalte wurde in '{output_file}' gespeichert.")
