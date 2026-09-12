import pytest

from app.models import Racket
from app.services.recommender import ANSWER_OPTIONS, WEIGHTS, recommend


def make_racket(**values):
    defaults = {
        "brand": "Test",
        "name": "Test Racket",
        "level": "beginner",
        "style": "control",
        "shape": "round",
        "weight_text": "350 g",
        "weight_avg": 350,
        "balance_text": "260 mm",
        "balance_mm": 260,
        "balance_group": "low",
        "price_text": "$100",
        "source_name": "Test source",
        "source_url": "https://example.com",
        "description": "Test data",
        "verified": True,
    }
    defaults.update(values)
    return Racket(**defaults)


def test_weights_are_explicit_and_sum_to_one():
    assert set(WEIGHTS) == {"level", "style", "priority", "weight", "balance"}
    assert sum(WEIGHTS.values()) == 1


def test_matching_racket_is_ranked_first_and_explained():
    exact = make_racket(name="Exact")
    power = make_racket(name="Power", style="power", shape="diamond", weight_avg=375, balance_group="high")
    answers = {"level": "beginner", "style": "control", "priority": "control", "weight": "light", "balance": "low"}

    results = recommend([power, exact], answers)

    assert [result.racket.name for result in results] == ["Exact", "Power"]
    assert results[0].score > results[1].score
    assert "совпадает стиль игры" in results[0].reasons


def test_scores_are_bounded_and_every_result_has_a_reason():
    rackets = [make_racket(name="A"), make_racket(name="B", style="power", shape="diamond")]
    answers = {"level": "advanced", "style": "attack", "priority": "power", "weight": "heavy", "balance": "high"}

    results = recommend(rackets, answers)

    assert all(0 <= result.score <= 100 for result in results)
    assert all(result.reasons for result in results)


def test_unknown_level_is_warning_not_positive_reason():
    answers = {"level": "beginner", "style": "control", "priority": "control", "weight": "light", "balance": "low"}
    result = recommend([make_racket(level="unknown")], answers)[0]
    assert result.warnings
    assert not any("уровень" in reason for reason in result.reasons)


def test_invalid_answers_and_limit_are_explicit_errors():
    answers = {key: next(iter(values)) for key, values in ANSWER_OPTIONS.items()}
    with pytest.raises(ValueError):
        recommend([make_racket()], {**answers, "weight": "invalid"})
    with pytest.raises(ValueError):
        recommend([], answers, limit=-1)
    assert recommend([], answers) == []
    assert recommend([make_racket()], answers, limit=0) == []


def test_ties_are_deterministic():
    answers = {key: next(iter(values)) for key, values in ANSWER_OPTIONS.items()}
    a, b = make_racket(name="A"), make_racket(name="B")
    assert [r.racket.name for r in recommend([b, a], answers)] == ["A", "B"]


def test_exact_fit_is_100_and_each_preference_can_change_ranking():
    answers = {"level": "beginner", "style": "control", "priority": "control", "weight": "light", "balance": "low"}
    assert recommend([make_racket()], answers)[0].score == 100
    for key, field, value, answer in [
        ("level", "level", "professional", "professional"),
        ("style", "style", "power", "attack"),
        ("priority", "style", "power", "power"),
        ("weight", "weight_avg", 375, "heavy"),
        ("balance", "balance_group", "high", "high"),
    ]:
        racket = make_racket(**{field: value})
        old = recommend([racket], answers)[0].score
        new = recommend([racket], {**answers, key: answer})[0].score
        assert new > old
