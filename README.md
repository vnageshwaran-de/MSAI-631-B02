# Hybrid Movie Recommendation System (MSAI-631-B02)

A hybrid movie recommender built for **MSAI-631 – Artificial Intelligence for
Human-Computer Interaction** (2026 Summer, second bi-term). It combines
item-based collaborative filtering with a genre-based content model and exposes
the results through two interfaces: a structured Gradio GUI and a small
conversational agent.

## What it does

- **Item-based collaborative filtering** on the MovieLens `ml-latest-small`
  ratings (100,836 ratings, 610 users), using mean-centered ("adjusted")
  cosine similarity.
- **Content-based filtering** using TF-IDF vectors over each movie's genre
  labels.
- **Hybrid blending**: a slider lets you weight the two signals anywhere from
  pure content-based (0.0) to pure collaborative (1.0).
- **Popularity damping** so thinly rated movies don't crowd out reliable
  recommendations.
- **Two interaction styles** (the HCI part): a dropdown-and-sliders GUI, and a
  chat tab where you can type things like *"movies like The Matrix"*.

## Running it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:7860 in a browser.

To sanity-check the engine without the GUI:

```bash
python recommender.py
```

## Files

| File | Purpose |
|---|---|
| `recommender.py` | Data loading, similarity models, hybrid scoring |
| `app.py` | Gradio GUI + conversational agent |
| `ml-latest-small/` | MovieLens dataset (GroupLens Research) |
| `requirements.txt` | Python dependencies |

## Credits

- Base approach adapted from Abhinav Ajitsaria's Real Python tutorial,
  *Build a Recommendation Engine With Collaborative Filtering*. My additions:
  the content-based TF-IDF component, the hybrid blend, mean-centering,
  popularity damping, and both user interfaces.
- Dataset: F. M. Harper & J. A. Konstan (2015), *The MovieLens Datasets:
  History and Context*, ACM TiiS 5(4). Used under the GroupLens usage license
  (non-commercial, with citation).
- Built with pandas, scikit-learn, and Gradio.
