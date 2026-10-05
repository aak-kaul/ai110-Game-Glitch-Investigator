import random
import streamlit as st

# FIX: Refactored game logic out of app.py into logic_utils.py using AI
# assistance; app.py now only handles the Streamlit UI.
from logic_utils import (
    TEMPERATURE_LABELS,
    check_guess,
    get_range_for_difficulty,
    get_temperature,
    parse_guess,
    update_high_score,
    update_score,
)


def show_hint_message(message, temperature):
    """Show a color-coded hint: red = hot, yellow = warm, blue = cold."""
    text = f"{message}  {TEMPERATURE_LABELS[temperature]}"
    if temperature == "Exact":
        st.success(text)
    elif temperature == "Hot":
        st.error(text)
    elif temperature == "Warm":
        st.warning(text)
    else:
        st.info(text)


def render_summary():
    """Show the session high score and a table of every valid guess."""
    st.subheader("📊 Session summary")
    col_high, col_score = st.columns(2)
    with col_high:
        high = st.session_state.high_score
        st.metric("🏆 High score", "—" if high is None else high)
    with col_score:
        st.metric("Current score", st.session_state.score)

    if st.session_state.guess_log:
        st.table(st.session_state.guess_log)
    else:
        st.caption("No guesses yet. Make one above!")


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: attempts used to start at 1, so "Attempts left" was off by one.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# FEATURE: High score tracker. It is NOT reset by New Game, so it keeps
# the best winning score for the whole browser session. Added with AI
# assistance.
if "high_score" not in st.session_state:
    st.session_state.high_score = None

# FEATURE: One row per valid guess, shown in the session summary table.
if "guess_log" not in st.session_state:
    st.session_state.guess_log = []

st.subheader("Make a guess")

# FIX: The prompt was hard-coded to "1 and 100"; it now uses the real range.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX: New Game now resets everything (status, score, history) and uses
    # the selected difficulty's range instead of always 1-100. Before, a won
    # or lost game stayed locked after clicking New Game.
    # The high score is kept on purpose.
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_log = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    render_summary()
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX: Removed the code that converted the secret to a string on even
        # attempts. That made comparisons lexicographic ("9" > "50") and
        # produced wrong hints on every other guess.
        secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)
        temperature = get_temperature(guess_int, secret, low, high)

        if show_hint:
            show_hint_message(message, temperature)

        st.session_state.guess_log.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": guess_int,
                "Result": outcome,
                "Closeness": TEMPERATURE_LABELS[temperature],
            }
        )

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.session_state.high_score = update_high_score(
                st.session_state.high_score, st.session_state.score
            )
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

render_summary()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
