# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from difflib import SequenceMatcher
from mistralai import Mistral
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# List of at least 20 songs
songs = [
    "Shape of You - Ed Sheeran",
    "Uptown Funk - Mark Ronson ft. Bruno Mars",
    "See You Again - Wiz Khalifa ft. Charlie Puth",
    "Sorry - Justin Bieber",
    "Blank Space - Taylor Swift",
    "Shake It Off - Taylor Swift",
    "Roar - Katy Perry",
    "Hello - Adele",
    "Thinking Out Loud - Ed Sheeran",
    "Sugar - Maroon 5",
    "Counting Stars - OneRepublic",
    "Closer - The Chainsmokers ft. Halsey",
    "Love Yourself - Justin Bieber",
    "What Do You Mean? - Justin Bieber",
    "Can't Stop The Feeling! - Justin Timberlake",
    "Bad Blood - Taylor Swift",
    "Believer - Imagine Dragons",
    "Thunder - Imagine Dragons",
    "Perfect - Ed Sheeran",
    "Stressed Out - Twenty One Pilots"
]

# Setup Mistral API client with the provided API key and model
api_key = "6mpmXb51sC0hMKPF1XpnSnLzXmA4bXwj"
model = "mistral-large-latest"
client = Mistral(api_key=api_key)


def generate_lyric_snippet(song_title: str) -> str:
    prompt = (
        f"Generate a short, evocative lyric snippet (2-4 lines) for the song titled '{song_title}', "
        "without directly revealing the song title. The lyrics should be creative and reminiscent of the song's mood."
    )
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        snippet = chat_response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback snippet in case of an error with the AI call
        snippet = "In the realm of dreams, where echoes play,\nA secret tune whispers, fading away."
    return snippet


def evaluate_with_fuzzy(user_guess: str, correct_title: str) -> float:
    """
    Computes a similarity ratio between the user's guess and the actual song name.
    The correct_title is assumed to be in the format "Song Title - Artist".
    """
    # Extract the song part (before the hyphen) and compare
    song_part = correct_title.split('-')[0].strip().lower()
    guess = user_guess.strip().lower()
    return SequenceMatcher(None, guess, song_part).ratio()


def evaluate_answer(user_guess: str, correct_title: str) -> str:
    """
    Uses fuzzy matching first and, if necessary, leverages the LLM for a dynamic evaluation.
    """
    ratio = evaluate_with_fuzzy(user_guess, correct_title)

    # If the similarity is high, return correct immediately.
    if ratio >= 0.8:
        return "correct"
    # If the similarity is very low, return incorrect.
    elif ratio < 0.5:
        return "incorrect"
    else:
        # In the gray zone, use LLM for evaluation.
        prompt = (
            f"Determine if the user's guess matches the correct song title. \n"
            f"Correct Song Title: \"{correct_title}\"\n"
            f"User Guess: \"{user_guess}\"\n\n"
            "Answer with only 'correct' or 'incorrect'."
        )
        try:
            chat_response = client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            evaluation = chat_response.choices[0].message.content.strip().lower()
            # Expecting a clear answer.
            if "correct" in evaluation and "incorrect" not in evaluation:
                return "correct"
            else:
                return "incorrect"
        except Exception as e:
            # Fallback to fuzzy matching decision in case of LLM error
            return "correct" if ratio >= 0.8 else "incorrect"


@app.get("/generate-lyric")
def get_lyric():
    # Randomly select a song from the list
    song_title = random.choice(songs)
    print(song_title)
    snippet = generate_lyric_snippet(song_title)
    return {"lyric_snippet": snippet, "song_title": song_title}


class AnswerCheck(BaseModel):
    user_guess: str
    correct_title: str


@app.post("/check-answer")
def check_answer(data: AnswerCheck):
    result = evaluate_answer(data.user_guess, data.correct_title)
    if result == "correct":
        return {"result": "correct"}
    else:
        return {"result": "incorrect", "correct_title": data.correct_title}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
