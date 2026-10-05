# 💭 Reflection: Game Glitch Investigator

## 1. What was broken when you started?

The game looked normal when I first ran it, but it was unwinnable in practice. The hints sent me the wrong way: when my guess was too high, the game told me to guess higher. Other guesses behaved strangely too, and Hard mode was easier than Normal. Most of these bugs don't crash anything, so I found them by playing the game and reading the code.

**Bug Reproduction Log**

| # | Input | Expected Behavior | Actual Behavior | Console Output / Error |
|---|-------|-------------------|-----------------|------------------------|
| 1 | Secret = 50, guess `60` | "Too High" with the hint "Go LOWER!" | The hint said "📈 Go HIGHER!" (the hint messages in `check_guess` were swapped) | No error, only a wrong hint in the UI. `check_guess(60, 50)` returned `("Too High", "📈 Go HIGHER!")` |
| 2 | Select **Hard** in the sidebar | Hard has a bigger range than Normal | Hard was 1–50, smaller than Normal's 1–100 (`get_range_for_difficulty`) | Sidebar showed "Range: 1 to 50" for Hard and "Range: 1 to 100" for Normal |
| 3 | Secret = 50, guess `9` on an even-numbered attempt | "Too Low" | `app.py` converted the secret to a string on even attempts, so the comparison became `"9" > "50"` and returned "Too High" | No error; `check_guess` silently fell into its `except TypeError` string-comparison branch |
| 4 | Win or lose, then click **New Game** | A fresh game starts | `status` stayed "won" or "lost", so the game stayed locked, and the new secret ignored the difficulty (always 1–100) | UI kept showing "Game over. Start a new game to try again." |
| 5 | Start any game | "Attempts left" equals the attempt limit | `attempts` started at 1, so Normal would show 7 instead of 8 attempts left (8 − 1); the prompt always said "1 and 100" | The prompt text was hard-coded in `app.py` |

| 6 | Secret = 5, guess `4` (attempt 1, Too Low), then guess `7` (attempt 2, Too High) | Each wrong guess lowers my score by 5, so the score should be -10 | The score went to -5 after attempt 1, then **up** to 0 after attempt 2 (`update_score` gave +5 for "Too High" on even attempts) | No error; the debug panel showed Score: -5 and then Score: 0 |

---

## 2. How did you use AI as a teammate?

I used Claude as my only AI tool on this project. I used it to refactor the logic into `logic_utils.py`, fix the bugs I marked with `FIXME` comments, and generate the pytest cases.

**Correct suggestion:** Claude suggested that the hint bug was a swapped-message problem inside `check_guess`, and that the fix was to return "Go LOWER!" when `guess > secret` and "Go HIGHER!" when `guess < secret`. It also pointed out that the `except TypeError` branch (which compared `str(guess)` to the secret) was hiding a second bug: `app.py` converted the secret to a string on even attempts, which made comparisons alphabetical. This was correct because my `FIXME` comments only covered the swapped messages, and removing the string conversion fixed the "every other guess is wrong" behavior too. I verified it with `test_too_high_hint_says_go_lower`, `test_too_low_hint_says_go_higher`, and `test_comparison_is_numeric_not_string` (`check_guess(9, 50)` must be "Too Low"), which all pass. I also checked it in the live game, where a guess of 100 against a secret of 77 now says "Go LOWER!" and a guess of 9 says "Go HIGHER!".

**Suggestion I did not accept as written:** While refactoring, a larger redesign was an option: replace the `"Win"` / `"Too High"` / `"Too Low"` strings with an `Enum` and wrap the Streamlit session state in a `GameState` class. I kept the plain tuple return of `(outcome, message)` and the existing string outcomes. The redesign was over-engineered for this lab, the starter tests and `update_score` already depend on those strings, and it would have made the diff much harder to review. I verified my smaller version by checking that `app.py` still imports the same four functions and that all 23 tests pass.

---

## 3. Debugging and testing your fixes

I treated a bug as fixed only when I had a test that reproduced it and I had also checked it in the live game. The starter tests were wrong too: they compared the result of `check_guess` to a string like `"Win"`, but the function returns `(outcome, message)`, so I changed them to unpack the tuple.

Tests I ran (23 total, all passing with `python -m pytest -v`):

- `test_too_high_hint_says_go_lower`: caught the swapped hint. It showed me that the message, not just the outcome label, needs a test.
- `test_hard_range_is_largest`: checks `Easy < Normal < Hard` instead of hard-coding numbers, so it still holds if the ranges change later.
- Edge cases for `parse_guess`: `"abc"`, `""`, `None`, `"-5"`, and `"42.9"` (decimals are truncated to 42).
- `test_too_high_always_loses_five_points`: checks attempts 1 to 4 so the old odd/even scoring quirk cannot come back.
- Later, tests for the hot/cold hints (`get_temperature`) and the high score (`update_high_score`), including a zero-width range and a negative first score.

```
collected 23 items

tests/test_game_logic.py::test_winning_guess PASSED                               [  4%]
tests/test_game_logic.py::test_guess_too_high PASSED                              [  8%]
tests/test_game_logic.py::test_guess_too_low PASSED                               [ 13%]
tests/test_game_logic.py::test_too_high_hint_says_go_lower PASSED                 [ 17%]
tests/test_game_logic.py::test_too_low_hint_says_go_higher PASSED                 [ 21%]
tests/test_game_logic.py::test_comparison_is_numeric_not_string PASSED            [ 26%]
tests/test_game_logic.py::test_hard_range_is_largest PASSED                       [ 30%]
tests/test_game_logic.py::test_ranges_start_at_one PASSED                         [ 34%]
tests/test_game_logic.py::test_parse_guess_non_numeric PASSED                     [ 39%]
tests/test_game_logic.py::test_parse_guess_empty_and_none PASSED                  [ 43%]
tests/test_game_logic.py::test_parse_guess_negative_number PASSED                 [ 47%]
tests/test_game_logic.py::test_parse_guess_decimal_is_truncated PASSED            [ 52%]
tests/test_game_logic.py::test_win_score_has_minimum_of_ten PASSED                [ 56%]
tests/test_game_logic.py::test_temperature_exact_guess PASSED                     [ 60%]
tests/test_game_logic.py::test_temperature_hot_when_very_close PASSED             [ 65%]
tests/test_game_logic.py::test_temperature_warm_when_moderately_close PASSED      [ 69%]
tests/test_game_logic.py::test_temperature_cold_when_far PASSED                   [ 73%]
tests/test_game_logic.py::test_temperature_scales_with_difficulty_range PASSED    [ 78%]
tests/test_game_logic.py::test_temperature_zero_width_range_does_not_crash PASSED [ 82%]
tests/test_game_logic.py::test_high_score_first_win_sets_it PASSED                [ 86%]
tests/test_game_logic.py::test_high_score_keeps_the_higher_value PASSED           [ 91%]
tests/test_game_logic.py::test_high_score_accepts_negative_first_score PASSED     [ 95%]
tests/test_game_logic.py::test_too_high_always_loses_five_points PASSED           [100%]

============================== 23 passed in 4.03s ==============================
```

AI helped me design the tests by suggesting that I assert on the hint text and not just the outcome label, and by suggesting edge cases for `parse_guess`.

I also played the live game with `streamlit run app.py` on Normal with the secret at 77. Guessing 100 gave "Go LOWER!", guessing 9 (an even attempt) gave "Go HIGHER!", and guessing 77 gave "Correct!" with a final score of 50. New Game then reset the score, attempts, and history and picked a new secret (97). Hard showed "Range: 1 to 200" with 5 attempts, and Easy showed "Range: 1 to 30" with 6 attempts.

While playing I noticed one thing I did not fix: the "Attempts left" box and the debug panel update one guess late because Streamlit draws them before the Submit button is handled. The hints and scoring were correct.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns your whole script from top to bottom every time you click a button or change a widget, so normal variables are reset on every rerun. `st.session_state` is a dictionary that survives those reruns, so anything that has to persist (the secret number, attempts, score, game status) must live there. The pattern `if "secret" not in st.session_state:` sets a value only once. That's also why New Game has to reset every key in session state, not just the secret: any key I forget keeps its old value, which was the cause of the locked "Game over" screen.

---

## 5. Looking ahead: your developer habits

- **Habit to reuse:** I want to keep marking suspected bugs with `FIXME` comments and then writing one small test per bug before trusting a fix. The tests also showed me a bug in the starter tests.
- **What I would do differently next time:** I would ask the AI to explain the whole data flow (UI → logic → session state) before asking for fixes, since two of the six bugs came from how `app.py` passed data to the logic functions, not from the logic itself.
- **How this changed my view of AI-generated code:** AI-generated code can look polished and still be quietly wrong, so I now read every diff and test behavior instead of trusting that it runs.
