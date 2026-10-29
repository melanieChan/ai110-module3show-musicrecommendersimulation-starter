# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

This system will recommend songs based on traits of the song that matches the user's preferences.

### `Song`

Each `Song` is a dataclass holding the fields loaded directly from `songs.csv`:

- `id`, `title`, `artist` — identity and display info, not used in scoring
- `genre` (str) — e.g. `pop`, `lofi`, `rock`
- `mood` (str) — e.g. `happy`, `chill`, `sad`
- `energy` (float, 0–1) — how intense/high-energy the track is; used in scoring
- `valence` (float, 0–1) — musical positivity; not separately weighted in scoring since it tracks `mood` closely (a `happy` song is already high-valence, a `sad` one low), so matching `mood` captures this signal
- `tempo_bpm`, `danceability`, `acousticness` (float) — `acousticness` is used via `likes_acoustic` matching; `tempo_bpm`/`danceability` are not separately weighted since they correlate closely with `energy`

### `UserProfile`

The `UserProfile` dataclass stores a compact taste profile rather than a full listening history:

- `favorite_genre` (str) — matched against `Song.genre`
- `favorite_mood` (str) — matched against `Song.mood`
- `target_energy` (float, 0–1) — the energy level the user wants, compared against `Song.energy`
- `likes_acoustic` (bool) — a simple toggle that nudges scoring toward higher-`acousticness` songs without needing another numeric weight

### `Recommender`

It will recommend songs based on engery, genre, mood, and acoustic preference. Although `songs.csv` offers more fields, some of those fields are similar to each other, so I would use only one from each group: energy, tempo_bpm, and danceability are similar, so I only use energy; valence is also similar to mood (a happy song is already high-valence), so mood alone captures that signal instead of scoring valence separately. A real world system would incoporate collaborative filtering and content based filtering, but since we don't have information on other users yet, it would mainly use content based filtering.

### Algorithm Recipe

This rule set `score_song()` uses to turn a `Song` + `UserProfile` pair into a single number, in order of how strongly each field should count.

| Signal | Rule | Points |
|---|---|---|
| Genre match | `song.genre == user.favorite_genre` | **+4** (all or nothing) |
| Mood match | `song.mood == user.favorite_mood` | **+3** (all or nothing) |
| Energy fit | how close `song.energy` is to `user.target_energy` | **up to +2**, scaled |
| Acoustic nudge | only applied if `user.likes_acoustic` is `True` | **up to +1**, scaled |

Max possible score: **10**. Min possible score: **0**.

**Why these weights:** genre and mood are treated as hard categorical preferences (a user picked one genre and one mood, so an exact match should dominate the score), while energy and acousticness are treated as soft, continuous signals — close-enough still counts for something, and they shouldn't be able to outweigh a genre/mood mismatch.

**Biases:**

- **Exact-string genre matching penalizes near-matches.** `genre` is compared with `==`, so a user who loves `pop` gets zero genre credit for `indie pop` or `synthwave` even though they're similar. This favors catalogs/users whose labels happen to line up exactly and penalizes hybrid or niche genre tags.
- **Genre + mood (7 of 10 points) dominate energy (2 points) by design.** This assumes that category labels matter more than how a song actually feels, so a song that matches genre and mood but has very different energy will almost always outrank a much better energy fit with a mismatched genre/mood — even for users who'd say vibe matters more than the label.
- **The acoustic nudge is one-directional.** `likes_acoustic=True` adds up to 1 point; there's no symmetric signal for someone who actively prefers non-acoustic/electronic songs. Users with that preference get no scoring benefit for it, even though it's just as real a taste signal.
- **A single genre/mood/energy/acoustic-flag can't represent eclectic taste.** The scoring assumes one favorite genre and one favorite mood per user, which flattens anyone with mixed or evolving taste into a single label they picked.
- **No diversity control in ranking.** Because songs are ranked purely by raw score, top-k results can cluster around the same artist or near-duplicate songs, reinforcing a narrow slice of the catalog rather than offering variety.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



