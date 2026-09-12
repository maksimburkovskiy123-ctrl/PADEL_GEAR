import re
from html import unescape
from urllib.parse import parse_qs, urlsplit

import pytest

ANSWERS = {"level": "beginner", "style": "control", "priority": "control",
           "weight": "light", "balance": "low"}




def test_home_page_is_available(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "моделей в каталоге" in response.text


def test_catalog_filter_returns_one_brand(client):
    response = client.get("/catalog?brand=Babolat")
    assert response.status_code == 200
    assert "Babolat" in response.text
    assert "Bullpadel Xplo PP26" not in response.text


def test_detail_and_compare_pages(client):
    detail = client.get("/rackets/1")
    compare = client.get("/compare?ids=1&ids=2")

    assert detail.status_code == 200
    assert "Источник" in detail.text
    assert compare.status_code == 200
    assert "Counter Veron 2.6" in compare.text
    assert "Technical Viper 3.0" in compare.text


def test_recommendation_flow_returns_ranked_models(client):
    response = client.get(
        "/recommendations?level=beginner&style=control&priority=control&weight=light&balance=low"
    )

    assert response.status_code == 200
    assert "Ваш результат" in response.text
    assert response.text.count("Открыть карточку") == 5


def test_empty_recommendation_redirects_to_form(client):
    response = client.get("/recommendations", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/recommend"


def test_compare_requires_two_models_and_limits_table_to_three(client):
    empty = client.get("/compare")
    too_many = client.get("/compare?ids=1&ids=2&ids=3&ids=4")

    assert empty.status_code == 200
    assert "недостаточно моделей" in empty.text
    assert too_many.status_code == 200
    assert "первые три" in too_many.text
    assert too_many.text.count("<th>") == 4


def test_unknown_racket_redirects_to_catalog(client):
    response = client.get("/rackets/9999", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/catalog"


def test_shape_filter_returns_only_matching_models(client):
    response = client.get("/catalog?shape=diamond")
    assert response.status_code == 200
    assert "Technical Viper 3.0" in response.text
    assert "Counter Origin" not in response.text


@pytest.mark.parametrize("field", list(ANSWERS))
@pytest.mark.parametrize("value", ["invalid", ""])
def test_invalid_answers_return_helpful_422(client, field, value):
    response = client.get("/recommendations", params={**ANSWERS, field: value})
    assert response.status_code == 422
    assert f'id="error-{field}"' in response.text
    assert response.context["answers"]["level"] == (value if field == "level" else "beginner")


def test_missing_answer_preserves_other_answers(client):
    response = client.get("/recommendations", params={k: v for k, v in ANSWERS.items() if k != "weight"})
    assert response.status_code == 422
    assert 'value="beginner" checked' in response.text
    assert 'id="error-weight"' in response.text


@pytest.mark.parametrize("group,expected", [("light", 4), ("medium", 10), ("heavy", 1)])
def test_weight_filters(client, group, expected):
    response = client.get("/catalog", params={"weight": group})
    assert response.status_code == 200
    assert len(response.context["rackets"]) == expected
    assert response.context["filters"]["weight"] == group


def test_filters_combine_and_survive_detail_roundtrip(client):
    filters = {"brand": "Babolat", "shape": "round", "weight": "light", "balance": "low"}
    catalog = client.get("/catalog", params=filters)
    assert [r.name for r in catalog.context["rackets"]] == ["Counter Origin"]
    detail_url = unescape(re.search(r'href="([^"]+)">Подробнее', catalog.text).group(1))
    detail = client.get(detail_url)
    back_url = unescape(re.search(r'class="back-link" href="([^"]+)"', detail.text).group(1))
    assert parse_qs(urlsplit(back_url).query) == {k: [v] for k, v in filters.items()}
    assert len(client.get(back_url).context["rackets"]) == 1


def test_compare_selection_uses_real_card_forms_and_survives_navigation(client):
    for racket_id in (1, 2):
        detail = client.get(f"/rackets/{racket_id}")
        action = unescape(re.search(r'<form method="post" action="([^"]+)"', detail.text).group(1))
        response = client.post(action)
        assert response.status_code == 200
        assert "Убрать из сравнения" in response.text
    client.get("/catalog?brand=Adidas")
    compare = client.get("/compare")
    assert [r.id for r in compare.context["rackets"]] == [1, 2]
    assert "Удалить" in compare.text and "Заменить" in compare.text


def test_comparison_limit_remove_and_replace(client):
    for racket_id in (1, 2, 3):
        client.post("/compare/toggle", params={"racket_id": racket_id})
    blocked = client.post("/compare/toggle", params={"racket_id": 4})
    assert "максимум три" in blocked.text
    assert blocked.context["selected_ids"] == [1, 2, 3]
    client.post("/compare/toggle", params={"racket_id": 2, "return_to": "/catalog"})
    client.post("/compare/toggle", params={"racket_id": 4})
    assert [r.id for r in client.get("/compare").context["rackets"]] == [1, 3, 4]


def test_duplicate_and_missing_comparison_ids_do_not_count(client):
    response = client.get("/compare?ids=1&ids=1&ids=9999")
    assert len(response.context["rackets"]) == 1
    assert "compare-table" not in response.text
    response = client.get("/compare?ids=9999&ids=1&ids=2&ids=3")
    assert [r.id for r in response.context["rackets"]] == [1, 2, 3]


def test_tampered_cookie_is_safe(client):
    client.cookies.set("compare_ids", "abc,1,1,9999,2")
    assert client.get("/compare").context["selected_ids"] == [1, 2]


@pytest.mark.parametrize("destination", ["//evil.example/", "https://evil.example/", "/\\evil.example/", "//[", "/not-a-page"])
def test_comparison_does_not_allow_external_redirects(client, destination):
    response = client.post("/compare/toggle", params={"racket_id": 1, "return_to": destination}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/catalog"
    assert "httponly" in response.headers["set-cookie"].lower()


def test_result_can_be_added_without_losing_answers(client):
    results = client.get("/recommendations", params=ANSWERS)
    action = unescape(re.search(r'<form method="post" action="([^"]+)"', results.text).group(1))
    added = client.post(action)
    assert added.status_code == 200
    assert added.context["answers"] == ANSWERS
    assert len(added.context["selected_ids"]) == 1


def test_separate_clients_do_not_share_comparison(client):
    from fastapi.testclient import TestClient
    from app.main import app

    client.post("/compare/toggle?racket_id=1")
    with TestClient(app) as other:
        assert other.get("/compare").context["selected_ids"] == []


def test_invalid_catalog_weight_is_rejected(client):
    assert client.get("/catalog?weight=invalid").status_code == 422
