import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        return [song for song in reader]

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    song_energy = float(song["energy"])
    song_acousticness = float(song.get("acousticness", 0))

    # Genre match: +4, all or nothing
    if song["genre"] == user_prefs["genre"]:
        score += 4
        reasons.append(f"Genre matches ({song['genre']})")

    # Mood match: +3, all or nothing
    if song["mood"] == user_prefs["mood"]:
        score += 3
        reasons.append(f"Mood matches ({song['mood']})")

    # Energy fit: up to +2, scaled by closeness to target energy
    target_energy = float(user_prefs["energy"])
    energy_points = max(0.0, 2 * (1 - abs(song_energy - target_energy)))
    score += energy_points
    reasons.append(
        f"Energy {song_energy:.2f} vs target {target_energy:.2f} (+{energy_points:.2f})"
    )

    # Acoustic nudge: up to +1, scaled, only if user likes acoustic songs
    if user_prefs.get("likes_acoustic"):
        acoustic_points = song_acousticness
        score += acoustic_points
        reasons.append(f"Acoustic nudge (+{acoustic_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))

    return sorted(scored, key=lambda result: result[1], reverse=True)[:k]
