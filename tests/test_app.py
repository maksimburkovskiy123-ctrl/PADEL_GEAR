from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page_is_available():
    response = client.get("/")
    assert response.status_code == 200
    assert "моделей в каталоге" in response.text


def test_catalog_filter_returns_one_brand():
    response = client.get("/catalog?brand=Babolat")
    assert response.status_code == 200
    assert "Babolat" in response.text
    assert "Bullpadel Xplo PP26" not in response.text


def test_detail_and_compare_pages():
    detail = client.get("/rackets/1")
    compare = client.get("/compare?ids=1&ids=2")

    assert detail.status_code == 200
    assert "Источник" in detail.text
    assert compare.status_code == 200
    assert "Counter Veron 2.6" in compare.text
    assert "Technical Viper 3.0" in compare.text


def test_recommendation_flow_returns_ranked_models():
    response = client.get(
        "/recommendations?level=beginner&style=control&priority=control&weight=light&balance=low"
    )

    assert response.status_code == 200
    assert "Ваш результат" in response.text
    assert response.text.count("Открыть карточку") == 5


def test_incomplete_recommendation_redirects_to_form():
    response = client.get("/recommendations", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/recommend"


def test_compare_requires_two_models_and_limits_table_to_three():
    empty = client.get("/compare")
    too_many = client.get("/compare?ids=1&ids=2&ids=3&ids=4")

    assert empty.status_code == 200
    assert "недостаточно моделей" in empty.text
    assert too_many.status_code == 200
    assert "первые три" in too_many.text
    assert too_many.text.count("<th>") == 4


def test_unknown_racket_redirects_to_catalog():
    response = client.get("/rackets/9999", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/catalog"


def test_shape_filter_returns_only_matching_models():
    response = client.get("/catalog?shape=diamond")
    assert response.status_code == 200
    assert "Technical Viper 3.0" in response.text
    assert "Counter Origin" not in response.text

