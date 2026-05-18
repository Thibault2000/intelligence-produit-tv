import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("reviews_with_topics.csv")

# Préparation des dates
df["at"] = pd.to_datetime(df["at"], errors="coerce")
df = df.dropna(subset=["at"])
df["year"] = df["at"].dt.year

st.sidebar.header("Filtres")

#Filtre temporel par année
min_year = int(df["year"].min())
max_year = int(df["year"].max())
year_range = st.sidebar.slider(
    "Période",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

#Filtre de source
st.sidebar.write("Source")
source_orange = st.sidebar.checkbox("OrangeTV", value=True)
source_oqee = st.sidebar.checkbox("Oqee", value=True)

#Filtre de version séparé par application
selected_orange_versions = []
selected_oqee_versions = []

# Récupération des versions disponibles pour chaque source
if source_orange:
    orange_versions = sorted(
        df.loc[df["source"] == "orange_tv", "appVersion"]
        .dropna()
        .astype(str)
        .unique()
    )
    selected_orange_versions = st.sidebar.multiselect(
        "Version OrangeTV",
        options=orange_versions,
        default=orange_versions
    )

if source_oqee:
    oqee_versions = sorted(
        df.loc[df["source"] == "oqee", "appVersion"]
        .dropna()
        .astype(str)
        .unique()
    )
    selected_oqee_versions = st.sidebar.multiselect(
        "Version Oqee",
        options=oqee_versions,
        default=oqee_versions
    )

# Application des filtres
filtered_df = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

source_masks = []

if source_orange:
    mask_orange = (
        (filtered_df["source"] == "orange_tv") &
        (filtered_df["appVersion"].astype(str).isin(selected_orange_versions))
    )
    source_masks.append(mask_orange)

if source_oqee:
    mask_oqee = (
        (filtered_df["source"] == "oqee") &
        (filtered_df["appVersion"].astype(str).isin(selected_oqee_versions))
    )
    source_masks.append(mask_oqee)

if source_masks:
    combined_mask = source_masks[0]
    for mask in source_masks[1:]:
        combined_mask = combined_mask | mask
    filtered_df = filtered_df[combined_mask]
else:
    filtered_df = filtered_df.iloc[0:0]

# KPI de synthèse en haut de page
if not filtered_df.empty:
    avg_score = filtered_df["score"].mean()
    avg_sentiment = filtered_df["sentiment_score"].mean()

    # Si sentiment_score est déjà sur 5, on le prend tel quel.
    # Sinon, adapte ici la normalisation avant de calculer le delta.
    sentiment_on_5 = avg_sentiment

    delta_sentiment = avg_score - sentiment_on_5

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Volume total d'avis analysés",
        f"{len(filtered_df):,}".replace(",", " ")
    )

    col2.metric(
        "Note moyenne",
        f"{avg_score:.2f}/5"
    )

    col3.metric(
        "Delta de sentiment",
        f"{delta_sentiment:+.2f}",
        help="Note moyenne des étoiles - score moyen du NLP ramené sur 5"
    )
else:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")

# Matrice de priorisation par topic
topic_matrix = (
    filtered_df[
        filtered_df["topic_name"].notna() &
        (filtered_df["topic_name"] != "outlier")
    ]
    .groupby("topic_name", as_index=False)
    .agg(
        frequency=("reviewId", "count"),
        severity=("sentiment_score", "mean")
    )
)

# Sécurité si le filtre ne renvoie rien
if not topic_matrix.empty:
    x_ref = topic_matrix["frequency"].median()
    y_ref = topic_matrix["severity"].median()

    fig = px.scatter(
        topic_matrix,
        x="frequency",
        y="severity",
        size="frequency",
        color="severity",
        hover_name="topic_name",
        size_max=45,
        color_continuous_scale="RdYlGn",
        labels={
            "frequency": "Fréquence",
            "severity": "Gravité moyenne",
        },
        title="Matrice de priorisation des sujets"
    )

    fig.add_vline(
        x=x_ref,
        line_width=2,
        line_dash="dash",
        line_color="gray"
    )
    fig.add_hline(
        y=y_ref,
        line_width=2,
        line_dash="dash",
        line_color="gray"
    )

    fig.update_traces(
        marker=dict(opacity=0.75, line=dict(width=1, color="white"))
    )

    fig.update_layout(
        xaxis_title="Fréquence des mentions",
        yaxis_title="Gravité moyenne (sentiment_score)",
        coloraxis_colorbar_title="Gravité",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Le quadrant en bas à droite correspond aux sujets très fréquents avec un sentiment très bas : ce sont les urgences absolues."
    )

# Benchmark concurrentiel: topics du quadrant bas droit
top_n = 6

topic_stats = (
    filtered_df[
        filtered_df["topic_name"].notna() &
        (filtered_df["topic_name"] != "outlier")
    ]
    .groupby("topic_name", as_index=False)
    .agg(
        total_count=("reviewId", "count"),
        severity=("sentiment_score", "mean")
    )
)

if not topic_stats.empty:
    x_ref = topic_stats["total_count"].median()
    y_ref = topic_stats["severity"].median()

    bottom_right_topics = topic_stats[
        (topic_stats["total_count"] >= x_ref) &
        (topic_stats["severity"] <= y_ref)
    ].sort_values("total_count", ascending=False).head(top_n)["topic_name"]

    topic_benchmark = (
        filtered_df[
            filtered_df["topic_name"].isin(bottom_right_topics) &
            filtered_df["topic_name"].notna() &
            (filtered_df["topic_name"] != "outlier")
        ]
        .groupby(["topic_name", "source"], as_index=False)
        .agg(review_count=("reviewId", "count"))
    )

    source_totals = (
        filtered_df[filtered_df["source"].isin(["orange_tv", "oqee"])]
        .groupby("source")["reviewId"]
        .count()
        .to_dict()
    )

    topic_benchmark["percent_reviews"] = topic_benchmark.apply(
        lambda row: (row["review_count"] / source_totals.get(row["source"], 1)) * 100,
        axis=1
    )

    if not topic_benchmark.empty:
        topic_benchmark["source"] = topic_benchmark["source"].map({
            "orange_tv": "OrangeTV",
            "oqee": "Oqee"
        })

        topic_order = list(bottom_right_topics)

        fig_benchmark = px.bar(
            topic_benchmark,
            x="topic_name",
            y="percent_reviews",
            color="source",
            barmode="group",
            text=topic_benchmark["percent_reviews"].round(1).astype(str) + "%",
            category_orders={"topic_name": topic_order},
            labels={
                "topic_name": "Topic",
                "percent_reviews": "% d'avis liés au topic",
                "source": "Source"
            },
            title="Benchmark concurrentiel des urgences absolues"
        )

        fig_benchmark.update_traces(textposition="outside")
        fig_benchmark.update_layout(
            xaxis_title="Topics du quadrant bas droit",
            yaxis_title="% d'avis liés au topic",
            template="plotly_white"
        )

        st.plotly_chart(fig_benchmark, use_container_width=True)

# Sélecteur de topic
available_topics = (
    filtered_df[
        filtered_df["topic_name"].notna() & (filtered_df["topic_name"] != "outlier")
    ]["topic_name"]
    .drop_duplicates()
    .sort_values()
    .tolist()
)

if available_topics:
    selected_topic = st.selectbox(
        "Choisir un topic",
        options=available_topics
    )

    topic_reviews = filtered_df[
        filtered_df["topic_name"] == selected_topic
    ][["content", "score", "appVersion", "source", "sentiment_score"]].sort_values(
        by="sentiment_score",
        ascending=True
    )

    st.subheader(f"Avis liés au topic : {selected_topic}")
    st.dataframe(
        topic_reviews[["content", "score", "appVersion", "source"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Aucun topic disponible avec les filtres actuels.")