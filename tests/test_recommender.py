from app.models import Racket
from app.services.recommender import WEIGHTS, recommend


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

