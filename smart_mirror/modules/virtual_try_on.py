from __future__ import annotations

from typing import Any

from smart_mirror import database


COLOR_PALETTES = {
    "warm": {
        "best": {"coral", "ivory", "olive", "gold", "terracotta", "mustard"},
        "okay": {"cream", "teal", "chocolate", "navy"},
    },
    "cool": {
        "best": {"rose", "blue", "emerald", "silver", "lavender", "berry"},
        "okay": {"navy", "white", "charcoal", "mint"},
    },
    "neutral": {
        "best": {"navy", "teal", "rose", "cream", "black", "sage"},
        "okay": {"coral", "blue", "olive", "white"},
    },
}

OCCASION_STYLES = {
    "casual": {"a-line", "shirt", "wrap", "denim"},
    "formal": {"sheath", "empire", "a-line", "satin"},
    "party": {"bodycon", "wrap", "satin", "a-line"},
    "work": {"sheath", "wrap", "a-line", "shirt"},
}

BODY_SHAPE_FIT = {
    "pear": {"a-line": 95, "wrap": 86, "empire": 80, "bodycon": 68, "sheath": 74},
    "hourglass": {"wrap": 95, "bodycon": 90, "sheath": 86, "a-line": 82, "empire": 76},
    "rectangle": {"empire": 88, "a-line": 84, "wrap": 82, "bodycon": 72, "sheath": 78},
    "apple": {"empire": 90, "wrap": 84, "a-line": 82, "sheath": 70, "bodycon": 62},
}


class VirtualTryOnModule:
    def match(self, payload: dict[str, Any], user_profile: dict[str, Any]) -> dict[str, Any]:
        color = str(payload.get("dominant_color", "coral")).strip().lower()
        occasion = str(payload.get("occasion", "party")).strip().lower()
        dress_cut = str(payload.get("dress_cut", "a-line")).strip().lower()
        body_shape = str(payload.get("body_shape") or user_profile.get("body_shape") or "pear").lower()
        undertone = str(user_profile.get("undertone", "neutral")).lower()

        color_score = self._color_score(color, undertone)
        occasion_score = self._occasion_score(dress_cut, occasion)
        body_score = BODY_SHAPE_FIT.get(body_shape, BODY_SHAPE_FIT["pear"]).get(dress_cut, 72)

        final_score = round(color_score * 0.65 + occasion_score * 0.20 + body_score * 0.15)
        suggestion = self._suggestion(final_score, color, dress_cut, occasion, undertone)

        database.insert_outfit_result(color, occasion, dress_cut, final_score, suggestion)

        return {
            "match_percentage": final_score,
            "breakdown": {
                "colour_harmony": color_score,
                "occasion_fit": occasion_score,
                "body_shape_fit": body_score,
            },
            "suggestion": suggestion,
            "rendering_note": "Prototype scoring only. Production would call a VTON model and return a composited image.",
        }

    @staticmethod
    def _color_score(color: str, undertone: str) -> int:
        palette = COLOR_PALETTES.get(undertone, COLOR_PALETTES["neutral"])
        if color in palette["best"]:
            return 94
        if color in palette["okay"]:
            return 78
        return 60

    @staticmethod
    def _occasion_score(dress_cut: str, occasion: str) -> int:
        if dress_cut in OCCASION_STYLES.get(occasion, set()):
            return 92
        return 68

    @staticmethod
    def _suggestion(score: int, color: str, dress_cut: str, occasion: str, undertone: str) -> str:
        metal = "gold" if undertone == "warm" else "silver" if undertone == "cool" else "mixed-metal"
        if score >= 85:
            return f"Strong match for {occasion}. Pair the {color} {dress_cut} dress with {metal} accessories and clean footwear."
        if score >= 70:
            return f"Good base look. Add {metal} accessories and a neutral layer to improve balance."
        return f"Try a different shade or cut for this occasion. A warmer/cooler accessory set may help, but the dress is not ideal."
