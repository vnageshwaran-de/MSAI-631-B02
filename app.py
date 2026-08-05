"""
Gradio GUI for the hybrid movie recommender (MSAI-631-B02).

Two ways to interact, reflecting the HCI focus of the course:
  1. A structured GUI tab: pick a movie from a searchable dropdown and
     adjust sliders for how many recommendations to show and how much to
     weight collaborative vs. content-based signals.
  2. A conversational tab: type something like "movies like The Matrix"
     and the agent parses the title out of the sentence and responds.

Run with:  python app.py   (opens at http://127.0.0.1:7860)
"""

import re

import gradio as gr

from recommender import MovieRecommender

rec = MovieRecommender()
ALL_TITLES = rec.titles()


# --------------------------------------------------------------------- #
# Tab 1: structured GUI
# --------------------------------------------------------------------- #
def gui_recommend(title, k, blend):
    if not title:
        return None, "Please choose a movie first."
    df = rec.recommend(title, k=int(k), blend=float(blend))
    mode = (
        "mostly collaborative filtering"
        if blend > 0.6
        else "mostly content-based" if blend < 0.4 else "an even hybrid"
    )
    note = f"Top {int(k)} picks for **{title}** using {mode} (blend = {blend:.2f})."
    return df, note


# --------------------------------------------------------------------- #
# Tab 2: conversational agent
# --------------------------------------------------------------------- #
GREETING = (
    "Hi! I'm a movie recommendation agent. Tell me a movie you liked — "
    "for example, *movies like Toy Story* or *I loved Inception* — and "
    "I'll suggest what to watch next."
)

PATTERNS = [
    r"(?:like|similar to|enjoyed|loved|liked|watch after)\s+(.+)",
    r"recommend(?:ations?)?\s+(?:for|based on)\s+(.+)",
]


def _extract_title(message: str) -> str:
    text = message.strip().rstrip("?!.")
    for pat in PATTERNS:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip().strip('"')
    return text  # assume the whole message is a title


def chat_respond(message, history):
    query = _extract_title(message)
    matches = rec.search(query)
    if not matches:
        return (
            f"I couldn't find anything matching “{query}”. "
            "Try including part of the exact title, e.g. *movies like Jumanji*."
        )
    title = matches[0]
    df = rec.recommend(title, k=5, blend=0.7)
    lines = [f"Because you mentioned **{title}**, you might enjoy:"]
    for _, row in df.iterrows():
        lines.append(f"- **{row['Title']}** ({row['Genres']}) — avg {row['Avg rating']}/5")
    if len(matches) > 1:
        others = ", ".join(matches[1:4])
        lines.append(f"\n*Did you mean a different movie? I also found: {others}.*")
    return "\n".join(lines)


# --------------------------------------------------------------------- #
# Layout
# --------------------------------------------------------------------- #
with gr.Blocks(title="Hybrid Movie Recommender — MSAI-631") as demo:
    gr.Markdown(
        "# 🎬 Hybrid Movie Recommender\n"
        "Item-based collaborative filtering blended with genre similarity, "
        "built on the MovieLens ml-latest-small dataset."
    )
    with gr.Tab("Recommender (GUI)"):
        with gr.Row():
            movie = gr.Dropdown(ALL_TITLES, label="Pick a movie you liked",
                                filterable=True)
        with gr.Row():
            k = gr.Slider(3, 20, value=10, step=1, label="How many recommendations")
            blend = gr.Slider(
                0.0, 1.0, value=0.7, step=0.05,
                label="Blend (0 = genres only, 1 = ratings only)",
            )
        btn = gr.Button("Recommend", variant="primary")
        note = gr.Markdown()
        table = gr.Dataframe(interactive=False)
        btn.click(gui_recommend, [movie, k, blend], [table, note])

    with gr.Tab("Ask the agent (chat)"):
        gr.ChatInterface(
            fn=chat_respond,
            chatbot=gr.Chatbot(
                value=[{"role": "assistant", "content": GREETING}],
                height=420,
            ),
        )

if __name__ == "__main__":
    demo.launch()
