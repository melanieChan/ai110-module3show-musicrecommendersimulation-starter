# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Song Recommender

---

## 2. Intended Use  

This recommender takes a short taste profile and returns a short, ranked list of songs from a fixed catalog that best match that profile, along with a plain-language reason for each pick.

It assumes the user can state their taste in those four terms, and that their stated genre and mood will line up with the exact labels already used in the catalog (e.g. typing `pop`, not `pop music` or `poppy`). It does not assume any listening history, feedback, or information about other users — it's a one-shot, content-based match between a single profile and a single catalog.

This is a classroom exploration project, not something built for real users. The catalog is 18 hand-picked songs, there's no input validation, and there's no persistence, accounts, or feedback loop. It's meant to demonstrate and critique how a simple scoring rule turns stated preferences into ranked output, not to actually recommend music to people.

---

## 3. How the Model Works  

Every song in the catalog has a genre, a mood, an energy level, and an "acousticness" value. A user's taste profile states one favorite genre, one favorite mood, a target energy level, and a yes/no on whether they like acoustic songs.

To score a song, the model hands out points in four pieces: a song gets a flat bonus if its genre exactly matches the user's favorite genre, another flat bonus if its mood exactly matches the user's favorite mood, a smaller bonus that slides up or down depending on how close the song's energy is to the user's target, and if the user said they like acoustic songs, a small extra bonus scaled to how acoustic the song actually is. All four pieces get added together into one score, every song in the catalog gets scored this way, and the songs are sorted from highest score to lowest. The top handful become the recommendations, each shown with a short explanation of which pieces of the score it earned and why.

The starter code only had placeholder logic (it just returned the first few songs in the file with no scoring at all). The change was writing the actual scoring rule described above and a weight-shift experiment to see how sensitive the rankings were to the point values chosen for each piece.

---

## 4. Data  

The catalog (`data/songs.csv`) has **18 songs**, each with a genre, a mood, and five numeric traits (energy, tempo, valence, danceability, acousticness). It started as a 10-song starter set and I expanded it by 8 more songs so that more genres and moods would be represented.

It now covers **15 genres** (ambient, classical, country, edm, folk, hip hop, indie pop, jazz, lofi, metal, pop, r&b, reggae, rock, synthwave) and **14 moods** (angry, carefree, chill, euphoric, focused, happy, intense, melancholic, moody, nostalgic, peaceful, relaxed, romantic, sad) across those 18 songs — almost every genre and mood appears in only one or two songs, so there's very little real competition within any single category.

Because the catalog is so small and hand-picked, it's missing a lot of what real musical taste involves: there's no concept of sub-genres or genre blends (a song is just one fixed genre label), no artist-level variety within a genre (most genres have exactly one song representing them), no lyrics or language signal at all, and no way to represent a listener who likes a mix of several genres or moods rather than one of each.

---

## 5. Strengths  

The system works best for a "clean" profile: a genre and mood that actually exist in the catalog, paired with a realistic (0-1) target energy. In the baseline test (`pop` / `happy` / energy `0.8`), the top result (`Sunrise City`) matched genre, mood, *and* energy almost exactly, and the rest of the rankings matched fewer criteria as expected.

It also handled a user with two genuinely compatible but non-obvious preferences well. The acoustic-lover-wants-metal profile (`metal` / `angry` / energy `0.95` / `likes_acoustic=True`) still correctly surfaced `Iron Verdict` (the actual metal/angry match) on top, because the acoustic nudge is small (max +1) relative to genre+mood (+7) — it can nudge the ranking without ever overriding a strong categorical match, which is the intended behavior.

---

## 6. Limitations and Bias 

The weight-shift experiment (genre halved to +2, energy doubled to +4) showed that it changes which kind of bias the system has, not whether it has one. With the original weights, the system is genre/mood-biased (a categorical match can outrank a much closer energy fit). After the shift, mid-ranking songs with no genre/mood match but close energy started outranking genre-only matches (e.g. in the baseline profile, `Rooftop Lights`, a mood-only match, jumped ahead of `Gym Hero`, a genre-only match, purely because of its closer energy). So the system is hard-coded to favor whichever preference has the highest weight.

Beyond the weight-shift finding, the stress-test profiles surfaced several structural biases:

- **Exact-string genre/mood matching has no concept of similarity.** A user who likes `pop` gets zero credit for `indie pop` — the scoring can't recognize similar genres or moods, so results are more rigid than a real listener's taste.
- **No validation on inputs.** An out-of-range energy (`1.5`, tested in one profile) is accepted and scored without complaint; the math still runs, but the number is meaningless, and nothing tells the user their input was invalid.
- **Silent fallback when there's no real match.** When genre/mood don't exist in the catalog at all (`opera` / `ecstatic`), the system doesn't flag "no good matches", it quietly ranks by energy alone and presents the result with the same confidence as a real match.
- **Single genre/single mood schema flattens eclectic taste.** `UserProfile` can only hold one favorite genre and one favorite mood, so any user who likes more than one of either cannot choose two or more.
- **The acoustic nudge is one-directional.** It can only reward high acousticness; there's no way to express or score a preference against acoustic songs.
- **No diversity control.** Because ranking is pure score-sort with no de-duplication, a top-k list can include multiple songs from the same artist, reinforcing a narrow slice of the catalog rather than offering variety.

---

## 7. Evaluation  

I tested five profiles against `recommend_songs()`: a **baseline** (`pop`/`happy`/`0.8`), an **adversarial conflicting-signal** profile (`hip hop`/`sad`/energy `0.9` — a "sad" mood paired with unusually high energy), an **edge-case profile with a genre/mood not present in the dataset** (`opera`/`ecstatic`), an **edge-case profile with an out-of-range energy** (`1.5`), and an **adversarial contradictory-taste** profile (wants `metal`/`angry` but also `likes_acoustic=True`). For each, I looked at whether the #1 recommendation made intuitive sense, whether the score breakdown explained the ranking honestly, and whether the system gave any signal when the input didn't really fit the catalog.

I was surprised that every profile, however nonsensical, returns a confident-looking top-5 with scores and explanations. The out-of-range energy and the nonexistent-genre profiles both produced plausible-looking output with no indication that the input was unusual. I also ran a simple weight-shift experiment on all five profiles: the #1 pick never changed in any profile, but the #2-#5 ordering shifted in 2 of 5 profiles, which told me the top pick is fairly robust to this specific reweighting, but the middle of the ranking is quite sensitive to it.

---

## 8. Future Work  

The most impactful next step would be letting a user express more than one genre or mood (and ideally a "dislikes acoustic" option, not just "likes"), since right now any eclectic taste gets flattened into a single label. I'd also want some notion of genre/mood similarity instead of exact-string matching, so `pop` and `indie pop` aren't treated as distinct.

For explanations, the current breakdown is accurate but doesn't tell the user when a recommendation is actually weak. I'd add a simple confidence label (e.g. "strong match" vs. "closest available, but no real genre/mood match") so the system stops presenting a desperate fallback with the same confidence as a great match, which was one of the problems the edge-case profiles surfaced.

For diversity, I'd add a simple cap on how many songs from the same artist can appear in one top-k list, to counter the filter-bubble effect from always ranking strictly by points.

For more complex user tastes, it would let different users weight genre/energy/mood differently based on their own priorities instead of using a single fixed-weight formula for all recommendations, and incorporating real listening history or collaborative filtering once there's data from more than one user.

---

## 9. Personal Reflection  

I was surprised that although there were many fields in songs.csv, for a simple recommender system I did not need all of them, and a few fields were redundant. It was also interesting that changing weights on certain traits didn't change the top recommendation in any of my test profiles, but it did reshuffle the #2-#5 results in 2 of 5 cases. It makes me curious how weights are determined in real recommendation systems, because there could be many reasons and tradeoffs for picking any particular configuration of weights.
