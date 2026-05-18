import pandas as pd
from transformers import pipeline
from tqdm import tqdm

# Feature engineering : ajout d'une colonne de score de sentiment (1-5) à partir du texte des avis
input_file = "reviews_cleaned.csv"
output_file = "reviews_with_sentiment.csv"
text_col = "content"

df = pd.read_csv(input_file, encoding="utf-8")

# Vérification de la présence de la colonne texte
if text_col not in df.columns:
    text_cols = df.select_dtypes(include=["object"]).columns
    if len(text_cols) == 0:
        raise ValueError("Aucune colonne texte trouvée dans le dataset.")
    text_col = text_cols[0]

# Chargement du modèle de classification de sentiment
classifier = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    truncation=True
)

# Application du modèle à chaque avis pour obtenir un score de sentiment
sentiments = []
for text in tqdm(df[text_col].fillna("").astype(str), desc="Sentiment analysis"):
    if not text.strip():
        sentiments.append(None)
        continue

    result = classifier(text[:512])[0]
    label = result["label"]  # ex: "4 stars"
    score = int(label.split()[0])
    sentiments.append(score)

df["sentiment_score"] = sentiments
df.to_csv(output_file, index=False, encoding="utf-8")