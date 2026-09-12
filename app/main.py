from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from .database import Base, engine, get_session
from .models import Racket
from .seed import seed_database
from .services.recommender import recommend


PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Padel Match")
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "app" / "static"), name="static")
templates = Jinja2Templates(directory=PROJECT_ROOT / "app" / "templates")

Base.metadata.create_all(engine)
with get_session() as startup_session:
    seed_database(startup_session)


LABELS = {
    "level": {
        "beginner": "Начальный",
        "intermediate": "Средний",
        "advanced": "Продвинутый",
        "professional": "Профессиональный",
        "unknown": "Не указан",
    },
    "style": {"control": "Контроль", "balanced": "Универсальный", "power": "Мощность", "attack": "Атака"},
    "shape": {
        "round": "Круглая",
        "teardrop": "Каплевидная",
        "diamond": "Алмазная",
        "hybrid": "Гибридная",
        "geometric": "Геометрическая",
        "allround": "All-round",
    },
    "balance": {"low": "Низкий", "even": "Средний", "high": "Высокий", "unknown": "Не указан"},
}


def page_context(**values):
    return {"labels": LABELS, **values}


@app.get("/", name="home")
def home(request: Request):
    with get_session() as session:
        count = session.scalar(select(func.count(Racket.id))) or 0
        brands = session.scalar(select(func.count(func.distinct(Racket.brand)))) or 0
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=page_context(count=count, brands=brands),
    )


@app.get("/catalog", name="catalog")
def catalog(
    request: Request,
    brand: str | None = None,
    level: str | None = None,
    shape: str | None = None,
    balance: str | None = None,
):
    with get_session() as session:
        query = select(Racket).order_by(Racket.brand, Racket.name)
        if brand:
            query = query.where(Racket.brand == brand)
        if level:
            query = query.where(Racket.level == level)
        if shape:
            query = query.where(Racket.shape == shape)
        rackets = list(session.scalars(query).all())
        brands = session.scalars(select(Racket.brand).distinct().order_by(Racket.brand)).all()
    if balance:
        rackets = [racket for racket in rackets if racket.balance_group == balance]
    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context=page_context(
            rackets=rackets,
            brands=brands,
            filters={"brand": brand or "", "level": level or "", "shape": shape or "", "balance": balance or ""},
        ),
    )


@app.get("/rackets/{racket_id}", name="racket_detail")
def racket_detail(request: Request, racket_id: int):
    with get_session() as session:
        racket = session.get(Racket, racket_id)
    if racket is None:
        return RedirectResponse(url="/catalog", status_code=303)
    return templates.TemplateResponse(request=request, name="racket_detail.html", context=page_context(racket=racket))


@app.get("/compare", name="compare")
def compare(request: Request, ids: list[int] = Query(default=[])):
    with get_session() as session:
        rackets = list(session.scalars(select(Racket).where(Racket.id.in_(ids[:3]))).all()) if ids else []
    ordered = {racket.id: racket for racket in rackets}
    rackets = [ordered[racket_id] for racket_id in ids[:3] if racket_id in ordered]
    return templates.TemplateResponse(
        request=request,
        name="compare.html",
        context=page_context(rackets=rackets, too_many=len(ids) > 3),
    )


@app.get("/recommend", name="recommend_form")
def recommend_form(request: Request):
    return templates.TemplateResponse(request=request, name="questionnaire.html", context=page_context())


@app.get("/recommendations", name="recommendations")
def recommendations(
    request: Request,
    level: str | None = None,
    style: str | None = None,
    priority: str | None = None,
    weight: str | None = None,
    balance: str | None = None,
):
    answers = {"level": level, "style": style, "priority": priority, "weight": weight, "balance": balance}
    if any(value is None for value in answers.values()):
        return RedirectResponse(url="/recommend", status_code=303)
    with get_session() as session:
        rackets = list(session.scalars(select(Racket)).all())
    results = recommend(rackets, answers)
    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context=page_context(results=results, answers=answers),
    )

