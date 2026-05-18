import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from stop_words import get_stop_words

# Feature engineering : ajout d'une colonne de topic à partir du texte des avis
input_file = "reviews_with_sentiment.csv"
output_file = "reviews_with_topics.csv"
text_col = "content"

df = pd.read_csv(input_file, encoding="utf-8")

# Vérification de la présence de la colonne texte
if text_col not in df.columns:
    text_cols = df.select_dtypes(include=["object"]).columns
    if len(text_cols) == 0:
        raise ValueError("Aucune colonne texte trouvée dans le dataset.")
    text_col = text_cols[0]

texts = df[text_col].fillna("").astype(str).tolist()

# Initialisation du modèle BERTopic avec un embedding multilingue et un vectorizer adapté au français
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
vectorizer_model = CountVectorizer(
    stop_words=list(get_stop_words("french")),
    ngram_range=(1, 2),
    min_df=2
)

# Création et entraînement du modèle BERTopic
topic_model = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    language="multilingual",
    calculate_probabilities=False,
    verbose=True
)

# Attribution d'un topic à chaque avis
topic_ids, _ = topic_model.fit_transform(texts)

def build_topic_name(topic_id, top_n=4):
    if topic_id == -1:
        return "outlier"

    words = topic_model.get_topic(topic_id)
    if not words:
        return "unknown"

    return " | ".join([word for word, _ in words[:top_n]])

df["topic_id"] = topic_ids
df["topic_name"] = [build_topic_name(tid) for tid in topic_ids]

df.to_csv(output_file, index=False, encoding="utf-8")

print(f"Dataset enrichi sauvegardé dans {output_file}")
print(df[["topic_id", "topic_name"]].head())