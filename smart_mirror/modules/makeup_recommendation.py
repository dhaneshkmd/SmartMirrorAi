from __future__ import annotations

from typing import Any


CONTOUR_RULES = {
    "round": "Contour the sides of the forehead, under cheekbones, and along the jawline. Highlight the center of the forehead and chin.",
    "oval": "Use light cheekbone contour and keep highlight balanced through the center of the face.",
    "square": "Soften the temples and jaw corners with contour. Keep blush rounded and blended upward.",
    "heart": "Contour the temples lightly and balance the chin with a soft highlight.",
    "long": "Keep contour near the hairline and chin. Place blush horizontally to shorten the face visually.",
}

BLUSH_BY_UNDERTONE = {
    "warm": "peach, coral, or warm terracotta",
    "cool": "rose, mauve, or soft berry",
    "neutral": "dusty rose, nude peach, or balanced pink",
}

EYE_RULES = {
    "almond": "Use a thin wing and deepen the outer V for natural lift.",
    "hooded": "Keep shimmer above the crease and use tightline liner to preserve lid space.",
    "round": "Extend liner outward and shade the outer third to elongate the eye.",
}


class MakeupRecommendationEngine:
    def build_plan(self, analysis: dict[str, Any]) -> dict[str, Any]:
        undertone = analysis.get("undertone", "neutral")
        face_shape = analysis.get("face_shape", "oval")
        eye_shape = analysis.get("eye_shape", "almond")
        coverage = "medium"

        if float(analysis.get("blemish_density", 0)) > 0.25:
            coverage = "full"
        elif float(analysis.get("blemish_density", 0)) < 0.1:
            coverage = "light"

        steps = [
            {
                "title": "Base",
                "detail": f"Use {coverage} coverage foundation in {analysis.get('foundation_shade', 'your closest shade')} with a {undertone} undertone match.",
            },
            {
                "title": "Concealer",
                "detail": "Apply one shade lighter under the eyes and spot-correct only where the blemish map is dense.",
            },
            {
                "title": "Contour and Highlight",
                "detail": CONTOUR_RULES.get(face_shape, CONTOUR_RULES["oval"]),
            },
            {
                "title": "Blush",
                "detail": f"Choose {BLUSH_BY_UNDERTONE.get(undertone, BLUSH_BY_UNDERTONE['neutral'])}; blend upward for a lifted finish.",
            },
            {
                "title": "Eyes",
                "detail": EYE_RULES.get(eye_shape, EYE_RULES["almond"]),
            },
            {
                "title": "Lips",
                "detail": self._lip_rule(analysis.get("lip_fullness", "balanced"), undertone),
            },
        ]

        return {
            "summary": "Personalized makeup routine generated from the latest face scan.",
            "steps": steps,
            "overlay_zones": self._overlay_zones(face_shape),
        }

    @staticmethod
    def _lip_rule(lip_fullness: str, undertone: str) -> str:
        family = {
            "warm": "caramel nude, peach rose, or brick",
            "cool": "rosewood, berry, or blue-red",
            "neutral": "pink nude, soft rose, or balanced red",
        }.get(undertone, "pink nude")

        if lip_fullness == "thin":
            return f"Slightly overline the cupid bow and center lower lip; use {family} with gloss at the center."
        if lip_fullness == "full":
            return f"Use a defined liner and satin finish in {family}."
        return f"Use a soft liner and balanced satin shade such as {family}."

    @staticmethod
    def _overlay_zones(face_shape: str) -> list[dict[str, str]]:
        return [
            {"zone": "forehead", "action": "highlight" if face_shape != "long" else "contour"},
            {"zone": "cheekbones", "action": "contour"},
            {"zone": "cheeks", "action": "blush"},
            {"zone": "chin", "action": "highlight" if face_shape != "long" else "contour"},
        ]
