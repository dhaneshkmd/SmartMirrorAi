from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class FaceAnalysis:
    face_shape: str
    skin_tone: str
    undertone: str
    lab: dict[str, float]
    foundation_shade: str
    skin_smoothness_score: int
    blemish_density: float
    eye_shape: str
    lip_fullness: str
    brow_arch: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


LAB_LOOKUP = {
    "fair": {"L": 78.0, "a": 9.0, "b": 14.0, "shade": "Porcelain 110"},
    "light": {"L": 70.0, "a": 11.0, "b": 18.0, "shade": "Light Beige 180"},
    "medium": {"L": 60.0, "a": 14.0, "b": 24.0, "shade": "Golden Beige 240"},
    "tan": {"L": 49.0, "a": 15.0, "b": 28.0, "shade": "Honey Tan 330"},
    "deep": {"L": 36.0, "a": 17.0, "b": 22.0, "shade": "Espresso 480"},
}


class FaceAnalysisModule:
    """Demo face analyzer.

    In production this class would consume camera frames, run MediaPipe Face Mesh,
    isolate skin regions, and classify landmarks. The prototype accepts optional
    user-provided hints and returns a realistic analysis object.
    """

    def analyze(self, payload: dict[str, Any]) -> FaceAnalysis:
        skin_tone = self._pick(payload.get("skin_tone"), LAB_LOOKUP.keys(), "medium")
        undertone = self._pick(
            payload.get("undertone"),
            ["warm", "cool", "neutral"],
            "warm",
        )
        face_shape = self._pick(
            payload.get("face_shape"),
            ["oval", "round", "square", "heart", "long"],
            "round",
        )

        lab_data = LAB_LOOKUP[skin_tone]
        blemish_density = float(payload.get("blemish_density", 0.18))
        smoothness = max(45, min(96, int(92 - blemish_density * 100)))

        return FaceAnalysis(
            face_shape=face_shape,
            skin_tone=skin_tone,
            undertone=undertone,
            lab={key: lab_data[key] for key in ["L", "a", "b"]},
            foundation_shade=lab_data["shade"],
            skin_smoothness_score=smoothness,
            blemish_density=round(blemish_density, 2),
            eye_shape=self._pick(payload.get("eye_shape"), ["almond", "hooded", "round"], "almond"),
            lip_fullness=self._pick(payload.get("lip_fullness"), ["thin", "balanced", "full"], "balanced"),
            brow_arch=self._pick(payload.get("brow_arch"), ["soft", "high", "straight"], "soft"),
        )

    @staticmethod
    def _pick(value: Any, allowed: Any, default: str) -> str:
        text = str(value or "").strip().lower()
        return text if text in allowed else default
