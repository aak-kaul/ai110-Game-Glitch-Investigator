"""Core game logic for Game Glitch Investigator.

Kept free of Streamlit imports so it can be unit tested with pytest.
"""

# Labels shown to the player for how close a guess is to the secret.
TEMPERATURE_LABELS = {
    "Exact": "🎯 Exact",
    "Hot": "🔥 Hot",
    "Warm": "🌤️ Warm",
    "Cold": "❄️ Cold",
}


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive (low, high) number range for a difficulty.

    Easy < Normal < Hard, so a harder level always has a bigger range.
    Unknown difficulties fall back to the Normal range.
    """
    # FIX: Hard used to be 1-50 (easier than Normal). Now Hard is the
    # widest range.
    # Found via FIXME in app.py; fixed with AI assistance and verified with
    # test_hard_range_is_largest in test_game_logic.py.
    if difficulty == "Easy":
        return 1, 30
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw: str):
    """Parse raw text input into an integer guess.

    Returns:
        (ok, guess_int, error_message)
        - ok: True if the input was a valid number
        - guess_int: the guess as an int (decimals are truncated), else None
        - error_message: a user-facing message, else None
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess to the secret and return (outcome, message).

    outcome is one of "Win", "Too High", "Too Low". The message tells the
    player which direction to move: a guess that is too high means they
    should go LOWER, and a guess that is too low means they should go HIGHER.
    """
    # FIX: Hint messages were swapped ("Too High" said "Go HIGHER").
    # FIX: Removed the old `except TypeError` branch that compared str(guess)
    # to the secret; app.py no longer passes the secret as a string, and
    # string comparison ("9" > "50") gave wrong answers anyway.
    # Refactored from app.py into logic_utils.py with AI assistance.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"

    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Return the new score after a guess.

    A win earns more points the fewer attempts were used (minimum 10).
    Every wrong guess (too high or too low) costs 5 points.
    """
    # FIX: A "Too High" guess used to add 5 points on even attempts and
    # subtract 5 on odd ones. It now always subtracts 5, like "Too Low".
    # Fixed with AI assistance; covered by
    # test_too_high_always_loses_five_points.
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def get_temperature(guess: int, secret: int, low: int, high: int):
    """Return how close a guess is to the secret as a temperature key.

    The distance is measured as a fraction of the difficulty's range so
    the same thresholds work for Easy, Normal, and Hard.

    Returns one of "Exact", "Hot" (within 10% of the range), "Warm"
    (within 30%), or "Cold" (anything farther). Use TEMPERATURE_LABELS to
    turn the key into the emoji label shown in the UI.
    """
    if guess == secret:
        return "Exact"

    span = max(high - low, 1)
    ratio = abs(guess - secret) / span

    if ratio <= 0.10:
        return "Hot"
    if ratio <= 0.30:
        return "Warm"
    return "Cold"


def update_high_score(current_high, new_score: int):
    """Return the higher of the stored high score and a new score.

    current_high is None when no game has been won yet in this session,
    in which case the new score becomes the high score (even if it is
    negative).
    """
    if current_high is None:
        return new_score
    return max(current_high, new_score)
