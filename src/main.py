"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    profiles = [
        (
            "Baseline",
            {"genre": "pop", "mood": "happy", "energy": 0.8},
        ),
        (
            "Adversarial: conflicting energy/mood (high energy + sad)",
            {"genre": "hip hop", "mood": "sad", "energy": 0.9},
        ),
        (
            "Edge case: genre/mood not in dataset",
            {"genre": "opera", "mood": "ecstatic", "energy": 0.6},
        ),
        (
            "Edge case: out-of-range target energy (> 1.0)",
            {"genre": "edm", "mood": "euphoric", "energy": 1.5},
        ),
        (
            "Adversarial: acoustic lover wants angry metal",
            {
                "genre": "metal",
                "mood": "angry",
                "energy": 0.95,
                "likes_acoustic": True,
            },
        ),
    ]

    for label, user_prefs in profiles:
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"=== Profile: {label} ===")
        print("User preferences:")
        for key, value in user_prefs.items():
            print(f"  {key}: {value}")

        print("\nTop recommendations:\n")
        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()
        print()


if __name__ == "__main__":
    main()
