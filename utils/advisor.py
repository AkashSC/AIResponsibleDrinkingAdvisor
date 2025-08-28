def grams_of_alcohol(volume_ml: float, abv_percent: float) -> float:
    return volume_ml * (abv_percent / 100) * 0.789

def estimate_bac_percent(grams_alcohol: float, body_weight_kg: float, gender: str, hours: float) -> float:
    r = 0.68 if gender.lower() == "m" else 0.55
    bac = (grams_alcohol / (body_weight_kg * r)) * 100 - (0.015 * hours)
    return max(bac, 0)

def advice_bundle(bac_pct: float, std_drinks_this_hour: float, asked_to_drive: bool) -> str:
    advice = []
    if bac_pct >= 0.08:
        advice.append("⚠️ You are above legal driving limit in most regions.")
    if std_drinks_this_hour > 2:
        advice.append("🚫 High consumption rate. Slow down.")
    if asked_to_drive:
        advice.append("❌ Do not drive under influence.")
    if not advice:
        advice.append("✅ You are within safe limits. Keep it moderate.")
    return " ".join(advice)

def classify_risk(bac_pct: float) -> str:
    if bac_pct < 0.03:
        return "low"
    elif bac_pct < 0.08:
        return "medium"
    else:
        return "high"
