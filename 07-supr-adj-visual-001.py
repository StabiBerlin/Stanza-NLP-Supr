import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Datei laden
file_path = "supr_df_enlarged.tsv"  # Passe den Pfad an

df = pd.read_csv(file_path, sep="\t")

# Prüfen, ob die notwendigen Spalten existieren
if "Label" not in df.columns or "POS" not in df.columns:
    raise ValueError("Die Datei muss die Spalten 'Label' und 'POS' enthalten.")

# Zählen der ADJ- und VERB-Tags pro Label
df["ADJ_Count"] = df["POS"].apply(lambda x: str(x).split().count("ADJ"))
df["VERB_Count"] = df["POS"].apply(lambda x: str(x).split().count("VERB"))

# Gruppieren nach Label und Summieren der Adjektive und Verben (Reihenfolge beibehalten)
adj_counts = df.groupby("Label", sort=False)["ADJ_Count"].sum()
verb_counts = df.groupby("Label", sort=False)["VERB_Count"].sum()

# Berechnung des relativen Mittelwerts zwischen Adjektiven und Verben
relative_mean = (adj_counts + verb_counts) / 2

# Labels auf 5 Wörter kürzen für die Anzeige
def shorten_label(label):
    return " ".join(label.split()[:5]) if len(label.split()) > 5 else label

short_labels = list(map(shorten_label, adj_counts.index))

# Plot erstellen
fig, ax1 = plt.subplots(figsize=(12, 6))

x = np.arange(len(short_labels))  # X-Positionen für Balken
width = 0.4  # Breite der Balken

# Balken für ADJ zeichnen
ax1.bar(x, adj_counts.values, width=width, label='Adjektive', alpha=0.7, color='skyblue', edgecolor='black')
ax1.set_ylabel("Anzahl der Adjektive", color='black', fontsize=10)
ax1.tick_params(axis='y', labelcolor='black', labelsize=10)
ax1.set_xticks(x)
ax1.set_xticklabels(short_labels, rotation=45, ha="right", color='black', fontsize=9)
ax1.grid(axis="y", linestyle="--", alpha=0.7)

# Zweite y-Achse für Verben erstellen
ax2 = ax1.twinx()
ax2.plot(x, verb_counts.values, label='Verben', color='red', marker='o', linestyle='-', linewidth=2)
ax2.set_ylabel("Anzahl der Verben", color='black', fontsize=10)
ax2.tick_params(axis='y', labelcolor='black', labelsize=10)

# Linie für den relativen Mittelwert einzeichnen
ax2.plot(x, relative_mean.values, label='Relativer Mittelwert', color='green', linestyle='--', linewidth=2)

# Legenden
ax1.legend(loc='upper left', fontsize=10)
ax2.legend(loc='upper right', fontsize=10)

plt.title("Abbildung 1: Anzahl der Adjektive und Verben pro Label mit Relativem Mittelwert", color='black', fontsize=12)
plt.savefig("adj_verb_visualization.png", dpi=400, bbox_inches="tight")
plt.savefig("adj_verb_visualization.svg", dpi=400, bbox_inches="tight") 
plt.show()
