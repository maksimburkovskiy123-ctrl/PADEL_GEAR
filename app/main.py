from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from urllib.parse import urlencode, urlsplit

from fastapi import FastAPI, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from . import database
from .database import Base, get_session
from .models import Racket
from .seed import seed_database
from .services.recommender import ANSWER_OPTIONS, recommend


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    url = database.engine.url
    if url.get_backend_name() == "sqlite" and url.database not in (None, "", ":memory:"):
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(database.engine)
    with get_session() as session:
        seed_database(session)
    yield


app = FastAPI(title="Padel Match", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "app" / "static"), name="static")
templates = Jinja2Templates(directory=PROJECT_ROOT / "app" / "templates")

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
    "weight": {"light": "До 355 г", "medium": "Более 355 до 370 г", "heavy": "Более 370 г"},
}


def safe_return_url(value: str, default: str = "/catalog") -> str:
    if not value.startswith("/") or "\\" in value or any(ord(char) <= 32 for char in value):
        return default
    try:
        url = urlsplit(value)
    except ValueError:
        return default
    allowed = url.path in {"/", "/catalog", "/compare", "/recommendations"}
    allowed = allowed or (url.path.startswith("/rackets/") and url.path[9:].isdigit())
    if url.scheme or url.netloc or not allowed:
        return default
    return url.path + ("?" + url.query if url.query else "")


def comparison_ids(request: Request) -> list[int]:
    ids = []
    for value in request.cookies.get("compare_ids", "")[:100].split(","):
        if value.isascii() and value.isdigit() and 0 < int(value) <= 2**31 - 1:
            if int(value) not in ids:
                ids.append(int(value))
    with get_session() as session:
        existing = set(session.scalars(select(Racket.id).where(Racket.id.in_(ids))))
    return [item for item in ids if item in existing][:3]


def save_comparison(response, request: Request, ids: list[int]):
    response.set_cookie("compare_ids", ",".join(map(str, ids)), httponly=True,
                        samesite="lax", secure=request.url.scheme == "https", max_age=86400)
    return response


def page_context(request: Request, **values):
    return {
        "labels": LABELS,
        "selected_ids": comparison_ids(request),
        "comparison_limit": request.query_params.get("notice") == "compare_limit",
        **values,
    }


@app.get("/", name="home")
def home(request: Request):
    with get_session() as session:
        count = session.scalar(select(func.count(Racket.id))) or 0
        brands = session.scalar(select(func.count(func.distinct(Racket.brand)))) or 0
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=page_context(request, count=count, brands=brands),
    )


@app.get("/catalog", name="catalog")
def catalog(
    request: Request,
    brand: str | None = None,
    level: str | None = None,
    shape: str | None = None,
    balance: str | None = None,
    weight: Literal["", "light", "medium", "heavy"] = "",
):
    with get_session() as session:
        query = select(Racket).order_by(Racket.brand, Racket.name)
        if brand:
            query = query.where(Racket.brand == brand)
        if level:
            query = query.where(Racket.level == level)
        if shape:
            query = query.where(Racket.shape == shape)
        if balance:
            query = query.where(Racket.balance_group == balance)
        if weight == "light":
            query = query.where(Racket.weight_avg <= 355)
        elif weight == "medium":
            query = query.where(Racket.weight_avg > 355, Racket.weight_avg <= 370)
        elif weight == "heavy":
            query = query.where(Racket.weight_avg > 370)
        rackets = list(session.scalars(query).all())
        brands = session.scalars(select(Racket.brand).distinct().order_by(Racket.brand)).all()
    filters = {"brand": brand or "", "level": level or "", "shape": shape or "",
               "balance": balance or "", "weight": weight}
    catalog_url = "/catalog?" + urlencode({key: value for key, value in filters.items() if value})
    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context=page_context(
            request,
            rackets=rackets,
            brands=brands,
            filters=filters,
            catalog_url=catalog_url.rstrip("?"),
        ),
    )


@app.get("/rackets/{racket_id}", name="racket_detail")
def racket_detail(request: Request, racket_id: int, return_to: str = "/catalog"):
    with get_session() as session:
        racket = session.get(Racket, racket_id)
    if racket is None:
        return RedirectResponse(url="/catalog", status_code=303)
    return_to = safe_return_url(return_to)
    if urlsplit(return_to).path != "/catalog":
        return_to = "/catalog"
    detail_url = f"/rackets/{racket_id}?" + urlencode({"return_to": return_to})
    return templates.TemplateResponse(request=request, name="racket_detail.html",
        context=page_context(request, racket=racket, return_to=return_to, detail_url=detail_url))


@app.get("/compare", name="compare")
def compare(request: Request, ids: list[int] | None = Query(default=None, max_length=100)):
    requested = list(dict.fromkeys(ids)) if ids is not None else comparison_ids(request)
    requested = [item for item in requested if 0 < item <= 2**31 - 1]
    with get_session() as session:
        rackets = list(session.scalars(select(Racket).where(Racket.id.in_(requested))))
    ordered = {racket.id: racket for racket in rackets}
    rackets = [ordered[item] for item in requested if item in ordered]
    too_many = len(rackets) > 3
    rackets = rackets[:3]
    selected_ids = [racket.id for racket in rackets]
    response = templates.TemplateResponse(
        request=request,
        name="compare.html",
        context=page_context(request, rackets=rackets, selected_ids=selected_ids, too_many=too_many),
    )
    return save_comparison(response, request, selected_ids)


@app.post("/compare/toggle", name="toggle_comparison")
def toggle_comparison(request: Request, racket_id: int = Query(gt=0, le=2**31 - 1),
                      return_to: str = "/catalog"):
    ids = comparison_ids(request)
    target = safe_return_url(return_to)
    with get_session() as session:
        racket = session.get(Racket, racket_id)
    if racket is None:
        return RedirectResponse("/catalog", status_code=303)
    if racket_id in ids:
        ids.remove(racket_id)
    elif len(ids) < 3:
        ids.append(racket_id)
    else:
        target += ("&" if "?" in target else "?") + "notice=compare_limit"
    return save_comparison(RedirectResponse(target, status_code=303), request, ids)


@app.get("/recommend", name="recommend_form")
def recommend_form(request: Request):
    return templates.TemplateResponse(request=request, name="questionnaire.html",
        context=page_context(request, answers={}, answer_options=ANSWER_OPTIONS, errors={}))


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
    if all(value is None for value in answers.values()):
        return RedirectResponse(url="/recommend", status_code=303)
    errors = {key: "Выберите один из предложенных вариантов."
              for key, options in ANSWER_OPTIONS.items() if answers[key] not in options}
    if errors:
        return templates.TemplateResponse(request=request, name="questionnaire.html", status_code=422,
            context=page_context(request, answers=answers, answer_options=ANSWER_OPTIONS, errors=errors))
    with get_session() as session:
        rackets = list(session.scalars(select(Racket)).all())
    results = recommend(rackets, answers)
    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context=page_context(request, results=results, answers=answers, answer_options=ANSWER_OPTIONS),
    )
