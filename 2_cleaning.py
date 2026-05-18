import pandas as pd

# Suppression des commentaires avec moins de 3 mots + normalisation de casse
input = "reviews.csv"
output = "reviews_cleaned.csv"
col = "content"

df = pd.read_csv(input, encoding="utf-8")

if col not in df.columns:
    text_cols = df.select_dtypes(include=["object"]).columns
    col = text_cols[0] if len(text_cols) else df.columns[0]

# Normaliser la casse (mettre en minuscule) et supprimer espaces autour
df[col] = df[col].fillna("").astype(str).str.strip().str.lower()

before = len(df)
df = df.drop_duplicates()
dups_removed = before - len(df)

def word_count(text):
    if pd.isna(text) or text == "": return 0
    return len(str(text).split())

mask = df[col].apply(word_count) >= 3
kept = df[mask]
removed_short = len(df) - mask.sum()

kept.to_csv(output, index=False, encoding="utf-8")

print(f"lignes initiales: {before}")
print(f"doublons stricts supprimés: {dups_removed}")
print(f"retenu >=3 mots: {len(kept)} lignes, supprimé: {removed_short} lignes")
print(f"résultat → {output}")

df_2 = pd.read_csv("reviews_cleaned.csv", encoding="utf-8")