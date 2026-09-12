from dataclasses import dataclass

from ..models import Racket


# Level and play style have the largest weights because they describe suitability
# before secondary preferences such as weight and balance.
WEIGHTS = {
    "level": 0.30,
    "style": 0.25,
    "priority": 0.20,
    "weight": 0.15,
    "balance": 0.10,
}


@dataclass(frozen=True)
class Recommendation:
    racket: Racket
    score: int
    reasons: list[str]


def _level_fit(user_level: str, racket_level: str) -> float:
    if racket_level == "unknown":
        return 0.6
    if user_level == racket_level:
        return 1.0
    adjacent = {
        ("beginner", "intermediate"),
        ("intermediate", "beginner"),
        ("intermediate", "advanced"),
        ("advanced", "intermediate"),
        ("advanced", "professional"),
        ("professional", "advanced"),
    }
    return 0.65 if (user_level, racket_level) in adjacent else 0.35


def _style_fit(user_style: str, racket_style: str) -> float:
    if user_style == "balanced":
        return {"balanced": 1.0, "control": 0.78, "power": 0.78}.get(racket_style, 0.65)
    if user_style == "control":
        return {"control": 1.0, "balanced": 0.78, "power": 0.45}.get(racket_style, 0.65)
    return {"power": 1.0, "balanced": 0.78, "control": 0.45}.get(racket_style, 0.65)


def _priority_fit(priority: str, racket: Racket) -> float:
    if priority == racket.style:
        return 1.0
    if priority == "maneuverability":
        return 1.0 if racket.weight_avg <= 360 and racket.shape in {"round", "teardrop", "allround"} else 0.55
    if priority == "control":
        return {"control": 1.0, "balanced": 0.78, "power": 0.45}.get(racket.style, 0.65)
    if priority == "power":
        return {"power": 1.0, "balanced": 0.78, "control": 0.45}.get(racket.style, 0.65)
    return 0.6


def _weight_fit(preference: str, weight_avg: float) -> float:
    target = {"light": 350, "medium": 365, "heavy": 375}[preference]
    return max(0.0, 1.0 - abs(weight_avg - target) / 30)


def _balance_fit(preference: str, balance_group: str) -> float:
    if balance_group == "unknown":
        return 0.6
    return 1.0 if preference == balance_group else 0.65


def recommend(rackets: list[Racket], answers: dict[str, str], limit: int = 5) -> list[Recommendation]:
    results = []
    for racket in rackets:
        components = {
            "level": _level_fit(answers["level"], racket.level),
            "style": _style_fit(answers["style"], racket.style),
            "priority": _priority_fit(answers["priority"], racket),
            "weight": _weight_fit(answers["weight"], racket.weight_avg),
            "balance": _balance_fit(answers["balance"], racket.balance_group),
        }
        score = round(sum(components[key] * WEIGHTS[key] for key in WEIGHTS) * 100)
        reasons = []
        if components["level"] >= 0.9:
            reasons.append("соответствует уровню")
        elif racket.level == "unknown":
            reasons.append("уровень не указан производителем")
        if components["style"] >= 0.9:
            reasons.append("совпадает стиль игры")
        if components["priority"] >= 0.9:
            reasons.append("совпадает главный приоритет")
        if components["weight"] >= 0.85:
            reasons.append("подходит выбранный вес")
        if components["balance"] >= 0.9:
            reasons.append("подходит баланс")
        if not reasons:
            reasons.append("наиболее близкое итоговое соответствие")
        results.append(Recommendation(racket=racket, score=score, reasons=reasons[:3]))
    return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

