"""
Hybrid movie recommendation engine for MSAI-631-B02.

Based on the collaborative filtering approach described in the Real Python
tutorial "Build a Recommendation Engine With Collaborative Filtering"
(Ajitsaria, 2024) and extended with:
  * a content-based component (TF-IDF over genre labels),
  * a tunable hybrid blend of the two scores,
  * popularity damping so obscure movies with 2 ratings don't dominate,
  * a clean API consumed by a Gradio GUI (app.py).

Dataset: MovieLens ml-latest-small (Harper & Konstan, 2015),
distributed by GroupLens Research at the University of Minnesota.
"""

import os
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), "ml-latest-small")

# Movies need at least this many ratings to be recommendable.
MIN_RATINGS = 20


class MovieRecommender:
    """Item-based collaborative filtering + genre content similarity."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.movies = pd.read_csv(os.path.join(data_dir, "movies.csv"))
        self.ratings = pd.read_csv(os.path.join(data_dir, "ratings.csv"))
        self._prepare()

    # ------------------------------------------------------------------ #
    # Model building
    # ------------------------------------------------------------------ #
    def _prepare(self) -> None:
        # Keep only movies with enough ratings for a stable similarity signal.
        counts = self.ratings.groupby("movieId")["rating"].agg(["count", "mean"])
        keep = counts[counts["count"] >= MIN_RATINGS].index
        self.movies = self.movies[self.movies["movieId"].isin(keep)].reset_index(drop=True)
        self.ratings = self.ratings[self.ratings["movieId"].isin(keep)]
        self.stats = counts.loc[keep].rename(columns={"count": "num_ratings", "mean": "avg_rating"})

        # --- Collaborative component: item-item cosine similarity ------- #
        user_item = self.ratings.pivot_table(
            index="movieId", columns="userId", values="rating"
        )
        # Mean-center each movie's ratings so similarity reflects taste,
        # not each movie's overall popularity level (adjusted cosine).
        centered = user_item.sub(user_item.mean(axis=1), axis=0).fillna(0.0)
        self.movie_ids = centered.index.to_numpy()
        self.cf_sim = cosine_similarity(centered.to_numpy())

        # --- Content component: TF-IDF over genre tokens ---------------- #
        genre_docs = (
            self.movies.set_index("movieId")
            .loc[self.movie_ids, "genres"]
            .str.replace("|", " ", regex=False)
            .str.replace("(no genres listed)", "unknown", regex=False)
        )
        tfidf = TfidfVectorizer(token_pattern=r"[A-Za-z-]+")
        self.content_sim = cosine_similarity(tfidf.fit_transform(genre_docs))

        # Fast lookups
        self._pos = {mid: i for i, mid in enumerate(self.movie_ids)}
        self._title_to_id = dict(
            zip(self.movies["title"].str.lower(), self.movies["movieId"])
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def titles(self):
        """All recommendable titles, sorted for the GUI dropdown."""
        return sorted(self.movies["title"].tolist())

    def search(self, text: str, limit: int = 15):
        """Loose substring search used by the chat-style text box."""
        pattern = re.escape(text.strip().lower())
        mask = self.movies["title"].str.lower().str.contains(pattern, na=False)
        return self.movies.loc[mask, "title"].head(limit).tolist()

    def recommend(self, title: str, k: int = 10, blend: float = 0.7) -> pd.DataFrame:
        """
        Return top-k recommendations for a seed movie.

        blend: weight on the collaborative score (0 = pure content-based,
               1 = pure collaborative filtering).
        """
        movie_id = self._title_to_id.get(title.strip().lower())
        if movie_id is None:
            matches = self.search(title)
            if not matches:
                raise ValueError(f"'{title}' was not found in the catalog.")
            movie_id = self._title_to_id[matches[0].lower()]
        i = self._pos[movie_id]

        score = blend * self.cf_sim[i] + (1.0 - blend) * self.content_sim[i]

        # Popularity damping: shrink scores of thinly-rated movies.
        n = self.stats.loc[self.movie_ids, "num_ratings"].to_numpy()
        score = score * (n / (n + MIN_RATINGS))
        score[i] = -np.inf  # never recommend the seed itself

        top = np.argsort(score)[::-1][:k]
        out = self.movies.set_index("movieId").loc[self.movie_ids[top]]
        result = pd.DataFrame(
            {
                "Title": out["title"].values,
                "Genres": out["genres"].str.replace("|", ", ", regex=False).values,
                "Similarity": np.round(score[top], 3),
                "Avg rating": np.round(
                    self.stats.loc[self.movie_ids[top], "avg_rating"].values, 2
                ),
                "# Ratings": self.stats.loc[self.movie_ids[top], "num_ratings"]
                .astype(int)
                .values,
            }
        )
        return result.reset_index(drop=True)


if __name__ == "__main__":
    rec = MovieRecommender()
    print("Loaded", len(rec.movie_ids), "movies.")
    print(rec.recommend("Toy Story (1995)", k=5).to_string(index=False))
