# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
