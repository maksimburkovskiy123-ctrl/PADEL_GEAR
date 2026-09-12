from sqlalchemy import select

from app.database import get_session
from app.models import Racket


def test_seed_catalog_has_expected_size_and_sources():
    with get_session() as session:
        rackets = list(session.scalars(select(Racket)).all())

    assert len(rackets) == 15
    assert {racket.brand for racket in rackets} == {"Adidas", "Babolat", "Bullpadel"}
    assert all(racket.verified for racket in rackets)
    assert all(racket.source_url.startswith("https://") for racket in rackets)

