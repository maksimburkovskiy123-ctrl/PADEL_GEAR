from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .models import Racket


RACKETS = [
    {
        "brand": "Babolat", "name": "Counter Veron 2.6", "level": "unknown", "style": "control",
        "shape": "round", "weight_text": "365 g +/- 10 g", "weight_avg": 365, "balance_text": "270 mm",
        "balance_mm": 270, "balance_group": "high", "price_text": "$260", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/counter-veron-2.6/150181.html",
        "description": "Counter Striker; круглая форма головы и баланс 270 мм по данным производителя.",
    },
    {
        "brand": "Babolat", "name": "Technical Viper 3.0", "level": "unknown", "style": "power",
        "shape": "diamond", "weight_text": "370 g +/- 10 g", "weight_avg": 370, "balance_text": "270 mm",
        "balance_mm": 270, "balance_group": "high", "price_text": "$390", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/technical-viper-3.0/150175.html",
        "description": "Technical Striker; ромбовидная форма головы и баланс 270 мм по данным производителя.",
    },
    {
        "brand": "Babolat", "name": "Counter Viper 2.6", "level": "unknown", "style": "control",
        "shape": "round", "weight_text": "365 g +/- 10 g", "weight_avg": 365, "balance_text": "270 mm",
        "balance_mm": 270, "balance_group": "high", "price_text": "$340", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/counter-viper-2.6/150177.html",
        "description": "Counter Striker; круглая форма головы и баланс 270 мм по данным производителя.",
    },
    {
        "brand": "Babolat", "name": "Technical Veron 3.0", "level": "unknown", "style": "power",
        "shape": "diamond", "weight_text": "360 g +/- 10 g", "weight_avg": 360, "balance_text": "270 mm",
        "balance_mm": 270, "balance_group": "high", "price_text": "$240", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/technical-veron-3.0/150183.html",
        "description": "Technical Striker; ромбовидная форма головы и баланс 270 мм по данным производителя.",
    },
    {
        "brand": "Babolat", "name": "Counter Vertuo 2.6", "level": "unknown", "style": "control",
        "shape": "round", "weight_text": "350 g +/- 10 g", "weight_avg": 350, "balance_text": "265 mm",
        "balance_mm": 265, "balance_group": "even", "price_text": "$200", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/counter-vertuo-2.6/150185.html?dwvar_150185_COLOR_DESCRIPTION_ERP=100",
        "description": "Counter Striker; круглая форма головы и баланс 265 мм по данным производителя.",
    },
    {
        "brand": "Babolat", "name": "Air Origin", "level": "unknown", "style": "balanced",
        "shape": "teardrop", "weight_text": "345 g +/- 10 g", "weight_avg": 345, "balance_text": "265 mm",
        "balance_mm": 265, "balance_group": "even", "price_text": "$140", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/air-origin/150153.html?dwvar_150153_COLOR_DESCRIPTION_ERP=100",
        "description": "Air Striker; каплевидная форма головы и баланс 265 мм по данным производителя.",
    },
    {
        "brand": "Babolat", "name": "Counter Origin", "level": "unknown", "style": "control",
        "shape": "round", "weight_text": "355 g +/- 10 g", "weight_avg": 355, "balance_text": "260 mm",
        "balance_mm": 260, "balance_group": "low", "price_text": "$120", "source_name": "Babolat",
        "source_url": "https://www.babolat.com/us/counter-origin/150154.html?dwvar_150154_COLOR_DESCRIPTION_ERP=100",
        "description": "Counter Striker; круглая форма головы и баланс 260 мм по данным производителя.",
    },
    {
        "brand": "Bullpadel", "name": "Xplo PP26", "level": "professional", "style": "power",
        "shape": "geometric", "weight_text": "365–375 g", "weight_avg": 370, "balance_text": "≈ 26.5 cm",
        "balance_mm": 265, "balance_group": "even", "price_text": "€379.99", "source_name": "Bullpadel",
        "source_url": "https://www.bullpadel.com/gb/5951-pala-bullpadel-xplo-pp26.html",
        "description": "Профессиональная модель; производитель указывает offensive style и geometric shape.",
    },
    {
        "brand": "Bullpadel", "name": "Wonder", "level": "professional", "style": "balanced",
        "shape": "hybrid", "weight_text": "350–360 g", "weight_avg": 355, "balance_text": "≈ 25.5 cm",
        "balance_mm": 255, "balance_group": "low", "price_text": "€199.98", "source_name": "Bullpadel",
        "source_url": "https://www.bullpadel.com/gb/5689-racket-bullpadel-wonder.html",
        "description": "Профессиональная versatile-модель; производитель указывает hybrid shape.",
    },
    {
        "brand": "Bullpadel", "name": "Neuron 02 Edge", "level": "professional", "style": "power",
        "shape": "geometric", "weight_text": "365–375 g", "weight_avg": 370, "balance_text": "≈ 26 cm",
        "balance_mm": 260, "balance_group": "low", "price_text": "€239.99", "source_name": "Bullpadel",
        "source_url": "https://www.bullpadel.com/gb/5685-racket-bullpadel-neuron-02-edge.html",
        "description": "Профессиональная модель; производитель указывает offensive style и geometric/diamond shape.",
    },
    {
        "brand": "Bullpadel", "name": "Icon 26", "level": "professional", "style": "power",
        "shape": "diamond", "weight_text": "370–375 g", "weight_avg": 372.5, "balance_text": "≈ 26 cm",
        "balance_mm": 260, "balance_group": "low", "price_text": "€209.99", "source_name": "Bullpadel",
        "source_url": "https://www.bullpadel.com/gb/5686-racket-bullpadel-icon-26.html",
        "description": "Профессиональная модель; производитель указывает offensive style и diamond shape.",
    },
    {
        "brand": "Bullpadel", "name": "Pearl 26", "level": "professional", "style": "power",
        "shape": "diamond", "weight_text": "355–365 g", "weight_avg": 360, "balance_text": "≈ 26 cm",
        "balance_mm": 260, "balance_group": "low", "price_text": "€209.99", "source_name": "Bullpadel",
        "source_url": "https://www.bullpadel.com/gb/5625-bullpadel-racket-pearl-26.html",
        "description": "Профессиональная модель; производитель указывает offensive style и diamond shape.",
    },
    {
        "brand": "Adidas", "name": "Arrow Hit", "level": "professional", "style": "power",
        "shape": "diamond", "weight_text": "360–375 g", "weight_avg": 367.5, "balance_text": "Head Heavy",
        "balance_mm": None, "balance_group": "high", "price_text": "€400", "source_name": "All For Padel",
        "source_url": "https://allforpadel.com/en/padel-rackets/7523-padel-racket-adidas-arrow-hit-8435739405888.html",
        "description": "PRO level; attack game, diamond shape и head-heavy balance по данным карточки производителя.",
    },
    {
        "brand": "Adidas", "name": "Arrow Hit CTRL", "level": "professional", "style": "control",
        "shape": "round", "weight_text": "360–375 g", "weight_avg": 367.5, "balance_text": "Even",
        "balance_mm": None, "balance_group": "even", "price_text": "€400", "source_name": "All For Padel",
        "source_url": "https://allforpadel.com/en/padel-rackets/7526-padel-racket-adidas-arrow-hit-ctrl-8435739405895.html",
        "description": "PRO level; round shape и even balance по данным карточки производителя.",
    },
    {
        "brand": "Adidas", "name": "Match Black 2026", "level": "beginner", "style": "balanced",
        "shape": "allround", "weight_text": "360–375 g", "weight_avg": 367.5, "balance_text": "Slightly Head Heavy",
        "balance_mm": None, "balance_group": "high", "price_text": "€75", "source_name": "All For Padel",
        "source_url": "https://allforpadel.com/en/padel-rackets/7493-padel-racket-adidas-match-black-2026-8435739406052.html",
        "description": "Beginner level; allround shape и slightly head-heavy balance по данным карточки производителя.",
    },
]


def seed_database(session: Session) -> None:
    if session.scalar(select(Racket.id).limit(1)) is None:
        session.add_all(Racket(**racket, verified=True) for racket in RACKETS)
    else:
        # One-time correction of known seed mistakes, not live price updates.
        # Preserve prices that were already changed manually.
        old_prices = {"Arrow Hit": "€160", "Arrow Hit CTRL": "€168", "Match Black 2026": "€234"}
        for item in RACKETS:
            if item["brand"] == "Adidas" and item["name"] in old_prices:
                session.execute(update(Racket).where(
                    Racket.brand == item["brand"], Racket.name == item["name"],
                    Racket.source_url == item["source_url"],
                    Racket.price_text == old_prices[item["name"]],
                ).values(price_text=item["price_text"]))
    session.commit()
