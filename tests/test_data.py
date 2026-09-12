from sqlalchemy import select

from app.database import get_session
from app.models import Racket


def test_seed_catalog_has_expected_size_and_sources(test_database):
    with get_session() as session:
        rackets = list(session.scalars(select(Racket)).all())

    assert len(rackets) == 15
    assert {racket.brand for racket in rackets} == {"Adidas", "Babolat", "Bullpadel"}
    assert all(racket.verified for racket in rackets)
    assert all(racket.source_url.startswith("https://") for racket in rackets)


def test_prices_correct_known_seed_mistakes_but_keep_manual_edits(test_database):
    from app.seed import seed_database

    with get_session() as session:
        items = {r.name: r for r in session.scalars(select(Racket).where(Racket.brand == "Adidas"))}
        assert {name: r.price_text for name, r in items.items()} == {
            "Arrow Hit": "€400", "Arrow Hit CTRL": "€400", "Match Black 2026": "€75"}
        items["Arrow Hit"].price_text = "€160"
        items["Arrow Hit CTRL"].price_text = "€168"
        items["Match Black 2026"].price_text = "€234"
        session.commit()
        seed_database(session)
        assert items["Arrow Hit"].price_text == "€400"
        assert items["Arrow Hit CTRL"].price_text == "€400"
        assert items["Match Black 2026"].price_text == "€75"
        items["Arrow Hit"].price_text = "€333"
        session.commit()
        seed_database(session)
        assert items["Arrow Hit"].price_text == "€333"
        assert len(list(session.scalars(select(Racket)))) == 15


def test_new_data_is_not_verified_by_default(test_database):
    from app.seed import RACKETS

    with get_session() as session:
        racket = Racket(**{**RACKETS[0], "name": "Unverified test row"})
        session.add(racket)
        session.commit()
        assert racket.verified is False
