from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    get_temperature,
    parse_guess,
    update_high_score,
    update_score,
)


# --- Starter tests (fixed: check_guess returns (outcome, message)) ---

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression tests for the bugs that were fixed ---

def test_too_high_hint_says_go_lower():
    # Bug: "Too High" used to tell the player to go HIGHER.
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_hint_says_go_higher():
    # Bug: "Too Low" used to tell the player to go LOWER.
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


def test_comparison_is_numeric_not_string():
    # Bug: the secret was sometimes cast to a string, so "9" > "50".
    # With ints, 9 is correctly Too Low against 50.
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


def test_hard_range_is_largest():
    # Bug: Hard (1-50) was smaller than Normal (1-100).
    easy_high = get_range_for_difficulty("Easy")[1]
    normal_high = get_range_for_difficulty("Normal")[1]
    hard_high = get_range_for_difficulty("Hard")[1]
    assert easy_high < normal_high < hard_high


def test_ranges_start_at_one():
    for level in ("Easy", "Normal", "Hard"):
        assert get_range_for_difficulty(level)[0] == 1


# --- Edge-case tests for parse_guess / update_score ---

def test_parse_guess_non_numeric():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_guess_empty_and_none():
    assert parse_guess("")[0] is False
    assert parse_guess(None)[0] is False


def test_parse_guess_negative_number():
    ok, value, err = parse_guess("-5")
    assert ok is True
    assert value == -5
    assert err is None


def test_parse_guess_decimal_is_truncated():
    ok, value, _ = parse_guess("42.9")
    assert ok is True
    assert value == 42


def test_win_score_has_minimum_of_ten():
    # A very late win should still award at least 10 points.
    assert update_score(0, "Win", 20) == 10


# --- Tests for the stretch features (hot/cold hints and high score) ---

def test_temperature_exact_guess():
    assert get_temperature(50, 50, 1, 100) == "Exact"


def test_temperature_hot_when_very_close():
    # 1 away on a 1-100 range is about 1% of the range.
    assert get_temperature(51, 50, 1, 100) == "Hot"


def test_temperature_warm_when_moderately_close():
    # 20 away on a 1-100 range is about 20% of the range.
    assert get_temperature(70, 50, 1, 100) == "Warm"


def test_temperature_cold_when_far():
    # 45 away on a 1-100 range is about 45% of the range.
    assert get_temperature(5, 50, 1, 100) == "Cold"


def test_temperature_scales_with_difficulty_range():
    # The same distance (10) is Cold on Easy but Warm on Hard.
    assert get_temperature(20, 10, 1, 30) == "Cold"
    assert get_temperature(120, 110, 1, 200) == "Hot"


def test_temperature_zero_width_range_does_not_crash():
    assert get_temperature(3, 5, 5, 5) == "Cold"


def test_high_score_first_win_sets_it():
    assert update_high_score(None, 50) == 50


def test_high_score_keeps_the_higher_value():
    assert update_high_score(80, 50) == 80
    assert update_high_score(50, 80) == 80


def test_high_score_accepts_negative_first_score():
    assert update_high_score(None, -10) == -10


def test_too_high_always_loses_five_points():
    # Bug: "Too High" used to add 5 points on even-numbered attempts.
    for attempt in range(1, 5):
        assert update_score(10, "Too High", attempt) == 5
