import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans

# Daten laden
df = pd.read_csv('supr_df_enlarged.tsv', sep='\t')
df = df.dropna(subset=['Lemmata']).reset_index(drop=True)

# TF-IDF-Vektorisierung (Trigramme)
tfidf_vectorizer = TfidfVectorizer(ngram_range=(3, 3))
tfidf_matrix = tfidf_vectorizer.fit_transform(df['Lemmata'])

# Berechnung der Kosinus-Ähnlichkeit
cosine_sim = cosine_similarity(tfidf_matrix)

# t-SNE-Dimensionsreduktion
tsne_model = TSNE(n_components=2, perplexity=30, max_iter=300, random_state=42)
tsne_result = tsne_model.fit_transform(cosine_sim)

# DataFrame mit t-SNE Ergebnissen
df_tsne = pd.DataFrame(tsne_result, columns=['x', 'y'], index=df.index)
df_tsne['Label'] = df['Label']

# K-Means Clustering
n_clusters = 6
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
df_tsne['Cluster'] = kmeans.fit_predict(tsne_result) + 1

# Ähnlichkeitswerte berechnen
similarity_scores = []
for cluster in range(1, n_clusters + 1):
    cluster_indices = df_tsne[df_tsne['Cluster'] == cluster].index
    if len(cluster_indices) > 1:
        cluster_sim_matrix = cosine_sim[np.ix_(cluster_indices, cluster_indices)]
        mean_sim = cluster_sim_matrix.mean(axis=1)
        max_sim = cluster_sim_matrix.max(axis=1)
        min_sim = np.min(cluster_sim_matrix, axis=1)
    else:
        mean_sim = [1.0]
        max_sim = [1.0]
        min_sim = [1.0]

    for idx, mean_s, max_s, min_s in zip(cluster_indices, mean_sim, max_sim, min_sim):
        similarity_scores.append((idx, mean_s, max_s, min_s))

# Merge der Ähnlichkeitswerte
df_sim = pd.DataFrame(similarity_scores, columns=['Index', 'Mean_Similarity', 'Max_Similarity', 'Min_Similarity'])
df_tsne = df_tsne.merge(df_sim, left_index=True, right_on='Index', how='left').drop(columns=['Index'])

# Speichern des finalen DataFrames
df_tsne['Label_ID'] = df.index
df_tsne.to_csv('clustered_labels_with_similarity.tsv', sep='\t', index=False)
print('Cluster-Zuordnung gespeichert: clustered_labels_with_similarity.tsv')

# Strukturierte Legende erstellen
legend_lines = []
for cluster, group in df_tsne.groupby('Cluster'):
    labels = df.loc[group.index, 'Label'].dropna().unique()
    labels_formatted = ', '.join(sorted(labels))
    wrapped_labels = "\n".join(textwrap.wrap(labels_formatted, width=80))
    legend_entry = f"Cluster {cluster}:\n{wrapped_labels}"
    legend_lines.append(legend_entry)

legend_text = "\n\n".join(legend_lines)

# Visualisierung
fig, ax = plt.subplots(figsize=(14, 9))
scatter = sns.scatterplot(data=df_tsne, x='x', y='y', hue='Cluster', palette='tab10', alpha=0.8, ax=ax)
plt.title(f"Abbildung 2: t-SNE Visualisierung mit K-Means Clustering ({n_clusters} Gruppen)")

# Standard-Legende für Cluster unter den Graphen setzen
handles, labels = scatter.get_legend_handles_labels()
ax.legend(handles, labels, title="Cluster", loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=n_clusters, fontsize=9)

# Legende mit Labels als separaten Textblock anzeigen
props = dict(boxstyle='round', facecolor='white', alpha=0.9)
ax.text(1.05, 0.5, legend_text, transform=ax.transAxes, fontsize=8,
        verticalalignment='center', bbox=props)

plt.tight_layout(rect=[0, 0, 0.75, 1])  # Platz für die strukturierte Legende reservieren
plt.savefig("tsne_clustering.png", dpi=400, bbox_inches="tight")  # Speichert mit 400 DPI
plt.savefig("tsne_clustering.svg", dpi=400, bbox_inches="tight")  # Speichert mit 400 DPI
plt.show()