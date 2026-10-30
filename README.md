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

Real-world music recommenders like Spotify or YouTube Music blend several kinds of signals to decide what to play next:

- **Input data** — raw facts about each item, independent of any one user: a song's genre, mood/valence, tempo, key, and audio features. For a video platform, this is metadata like category, length, and captions.
- **User preferences** — what a specific listener seems to want, usually inferred rather than stated outright: listening history, skip/replay/like behavior, time of day, and similarity to other users with overlapping taste (collaborative filtering).
- **Ranking/selection** — turning (input data + user preferences) into an ordered list: candidate items are scored against the inferred preference profile, then sorted and truncated to a top-N list, often with extra business logic layered on top (diversity, freshness, promoted content).

This project is a deliberately simplified version of that same pipeline:

- **Input data** → the song catalog in `data/songs.csv` (genre, mood, energy, tempo, valence, danceability, acousticness).
- **User preferences** → `UserProfile`, but stated directly by the user (favorite genre/mood, target energy, acoustic preference) instead of inferred from listening history, since there's no behavioral data to learn from.
- **Ranking/selection** → `score_song()` scores every song against that profile, and `recommend_songs()` sorts and returns the top-k.

Because there's no listening history or other users to compare against, this system is purely **content-based filtering** (matching item features to a stated profile), not **collaborative filtering** (matching users to similar users) — real systems like Spotify combine both, but collaborative filtering only becomes possible once you have data from many users' behavior, which this project doesn't have.

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

### One user profile:

```
Loading songs from data/songs.csv...
User preferences:
  genre: pop
  mood: happy
  energy: 0.8

Top recommendations:

Sunrise City - Score: 8.96
Because: Genre matches (pop), Mood matches (happy), Energy 0.82 vs target 0.80 (+1.96)

Gym Hero - Score: 5.74
Because: Genre matches (pop), Energy 0.93 vs target 0.80 (+1.74)

Rooftop Lights - Score: 4.92
Because: Mood matches (happy), Energy 0.76 vs target 0.80 (+1.92)

Night Drive Loop - Score: 1.90
Because: Energy 0.75 vs target 0.80 (+1.90)

Storm Runner - Score: 1.78
Because: Energy 0.91 vs target 0.80 (+1.78)
```

### Multiple user profiles:
```
Loading songs from data/songs.csv...
=== Profile: Baseline ===
User preferences:
  genre: pop
  mood: happy
  energy: 0.8

Top recommendations:

Sunrise City - Score: 8.96
Because: Genre matches (pop), Mood matches (happy), Energy 0.82 vs target 0.80 (+1.96)

Gym Hero - Score: 5.74
Because: Genre matches (pop), Energy 0.93 vs target 0.80 (+1.74)

Rooftop Lights - Score: 4.92
Because: Mood matches (happy), Energy 0.76 vs target 0.80 (+1.92)

Night Drive Loop - Score: 1.90
Because: Energy 0.75 vs target 0.80 (+1.90)

Storm Runner - Score: 1.78
Because: Energy 0.91 vs target 0.80 (+1.78)


=== Profile: Adversarial: conflicting energy/mood (high energy + sad) ===
User preferences:
  genre: hip hop
  mood: sad
  energy: 0.9

Top recommendations:

Broken Compass - Score: 8.10
Because: Genre matches (hip hop), Mood matches (sad), Energy 0.45 vs target 0.90 (+1.10)

Storm Runner - Score: 1.98
Because: Energy 0.91 vs target 0.90 (+1.98)

Gym Hero - Score: 1.94
Because: Energy 0.93 vs target 0.90 (+1.94)

Iron Verdict - Score: 1.88
Because: Energy 0.96 vs target 0.90 (+1.88)

Pulse Overdrive - Score: 1.86
Because: Energy 0.97 vs target 0.90 (+1.86)


=== Profile: Edge case: genre/mood not in dataset ===
User preferences:
  genre: opera
  mood: ecstatic
  energy: 0.6

Top recommendations:

Dusty Highway - Score: 1.90
Because: Energy 0.55 vs target 0.60 (+1.90)

Velvet Hours - Score: 1.80
Because: Energy 0.50 vs target 0.60 (+1.80)

Broken Compass - Score: 1.70
Because: Energy 0.45 vs target 0.60 (+1.70)

Island Ease - Score: 1.70
Because: Energy 0.45 vs target 0.60 (+1.70)

Night Drive Loop - Score: 1.70
Because: Energy 0.75 vs target 0.60 (+1.70)


=== Profile: Edge case: out-of-range target energy (> 1.0) ===
User preferences:
  genre: edm
  mood: euphoric
  energy: 1.5

Top recommendations:

Pulse Overdrive - Score: 7.94
Because: Genre matches (edm), Mood matches (euphoric), Energy 0.97 vs target 1.50 (+0.94)

Iron Verdict - Score: 0.92
Because: Energy 0.96 vs target 1.50 (+0.92)

Gym Hero - Score: 0.86
Because: Energy 0.93 vs target 1.50 (+0.86)

Storm Runner - Score: 0.82
Because: Energy 0.91 vs target 1.50 (+0.82)

Sunrise City - Score: 0.64
Because: Energy 0.82 vs target 1.50 (+0.64)


=== Profile: Adversarial: acoustic lover wants angry metal ===
User preferences:
  genre: metal
  mood: angry
  energy: 0.95
  likes_acoustic: True

Top recommendations:

Iron Verdict - Score: 9.03
Because: Genre matches (metal), Mood matches (angry), Energy 0.96 vs target 0.95 (+1.98), Acoustic nudge (+0.05)

Storm Runner - Score: 2.02
Because: Energy 0.91 vs target 0.95 (+1.92), Acoustic nudge (+0.10)

Gym Hero - Score: 2.01
Because: Energy 0.93 vs target 0.95 (+1.96), Acoustic nudge (+0.05)

Pulse Overdrive - Score: 1.98
Because: Energy 0.97 vs target 0.95 (+1.96), Acoustic nudge (+0.02)

Rooftop Lights - Score: 1.97
Because: Energy 0.76 vs target 0.95 (+1.62), Acoustic nudge (+0.35)
```

---

## Experiments You Tried

**Stress-testing with diverse profiles.** I ran five profiles through `recommend_songs()` beyond the starter example: a baseline (`pop`/`happy`/energy `0.8`); an adversarial profile with conflicting signals (`hip hop`/`sad`/energy `0.9` — unusually high energy for a "sad" mood); an edge case with a genre/mood not present in the catalog at all (`opera`/`ecstatic`); an edge case with an out-of-range target energy (`1.5`, above the valid 0-1 scale); and an adversarial profile with contradictory taste (wants `metal`/`angry` but also `likes_acoustic=True`, even though metal songs in this catalog have near-zero acousticness). All five ran without errors and produced a ranked top-5, but the two edge cases revealed that the system never flags bad input — it just quietly scores whatever it's given (see Limitations below).

**Weight shift: genre halved, energy doubled.** For the experiment, I changed `score_song()`'s genre-match weight from `+4` to `+2` and the max energy-fit score from `+2` to `+4`, then re-ran all five profiles. Results:

- The **#1 recommendation never changed** in any profile — when a song matches genre, mood, *and* energy, it wins by a wide enough margin that this specific reweighting didn't flip the top pick.
- The **#2-#5 ordering shifted in 2 of 5 profiles**. In the baseline, `Rooftop Lights` (mood-only match, energy 0.76) jumped from #3 to #2, overtaking `Gym Hero` (genre-only match, energy 0.93) — because energy-closeness now outweighs a genre match alone. The same pattern appeared in the acoustic/metal profile.
- **Takeaway:** reweighting doesn't remove a bias, it relocates it. The original weights favor a "genre/mood bubble" (category labels dominate); doubling energy's weight instead favors an "energy/tempo bubble" (songs that *feel* similar can now outrank songs that are categorically correct).

---

## Limitations and Risks

- **Tiny, hand-curated catalog (18 songs).** Most genre/mood combinations appear in at most one or two songs, so there's rarely real competition within a category — the ranking logic hasn't been tested against a catalog where many songs plausibly tie.
- **No input validation.** Energy values outside 0-1, or a genre/mood string that doesn't exist in the catalog, are accepted and scored anyway. The system has no way to tell a user "none of this really matches" — it just returns its best-effort top-5 with the same confident formatting every time, which risks misleading a user into thinking a weak match is a strong one.
- **Exact-match-only genre/mood comparison.** `pop` and `indie pop` are treated as completely unrelated, so the system can't recognize near-misses or hybrid genres — it's more rigid than real musical taste.
- **One genre + one mood per user.** The `UserProfile` schema can't represent someone who likes more than one genre or is open to more than one mood, so eclectic listeners get flattened into a single label.
- **It does not understand lyrics, language, or any audio content directly** — all scoring is based on the numeric/categorical metadata in `songs.csv`, not the music itself.

---

## Reflection

I learned that recommenders can use weights to give specific traits more impact in the scoring. Bias or unfairness could show up in systems like this when the specific weights for certain traits are fixed in the system, because different users may have different priorities for which traits should hold more or less weight. By having all recommendations use the same fixed weights determined by the system, the recommendations could be less catered toward the users' preferences.

Testing this system also showed me that a real, more complex recommender would need a lot more than four variables to actually capture someone's taste, things like genre and mood similarity, listening history, and complex preferences.

