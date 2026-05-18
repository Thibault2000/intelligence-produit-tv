import csv
import pandas as pd
from google_play_scraper import reviews_all, Sort

# Maximum d'avis à extraire par application
MAX_REVIEWS = 5000

# Extraction des avis pour les deux applications et sauvegarde dans des fichiers CSV séparés
apps = [
    {
        "app_id": "com.orange.owtv",
        "output": "orange_tv_reviews.csv"
    },
    {
        "app_id": "net.oqee.androidmobile",
        "output": "oqee_reviews.csv"
    },
]

# Boucle d'extraction pour chaque application
for app in apps:
    reviews = reviews_all(
        app["app_id"],
        lang='fr',
        country='fr',
    sort=Sort.NEWEST
)

    reviews_comments = [
        review for review in reviews
        if (review.get("content") or "").strip()
    ]

    # Limiter le nombre d'avis écrits à MAX_REVIEWS (par application)
    reviews_comments = reviews_comments[:MAX_REVIEWS]

    with open(app["output"], 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["reviewId","appVersion" , "score", "at", "content"], quoting=csv.QUOTE_ALL,)
        writer.writeheader()

        for review in reviews_comments:
            writer.writerow({
                "reviewId": review.get('reviewId'),
                "appVersion": review.get('appVersion'),
                "score": review.get('score'),
                "at": review.get('at'),
                "content": review.get('content')
            })

# Fusion des deux fichiers CSV en un seul fichier "reviews.csv" avec une colonne "source" indiquant la provenance de chaque avis
inputs = [("orange_tv_reviews.csv", "orange_tv"), ("oqee_reviews.csv", "oqee")]
dfs = []
for path, source in inputs:
    df = pd.read_csv(path, encoding="utf-8")
    df["source"] = source
    dfs.append(df)

pd.concat(dfs, ignore_index=True).to_csv("reviews.csv", index=False, quoting=csv.QUOTE_ALL)