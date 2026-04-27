from __future__ import annotations

from typing import Any

from smart_mirror import database


class ProductScannerModule:
    def scan(self, payload: dict[str, Any], user_profile: dict[str, Any]) -> dict[str, Any]:
        barcode = str(payload.get("barcode", "")).strip()
        query = str(payload.get("query", "")).strip()

        product = None
        mode = "barcode" if barcode else "ocr"

        if barcode:
            product = database.fetch_product_by_barcode(barcode)
        if product is None and query:
            product = database.search_product_by_text(query)

        if product is None:
            return {
                "found": False,
                "mode": mode,
                "message": "No product found. Add it manually or connect an external product API.",
            }

        return {
            "found": True,
            "mode": mode,
            "product": product,
            "compatibility": self._compatibility_score(product, user_profile),
        }

    @staticmethod
    def _compatibility_score(product: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
        score = 55
        reasons = []

        if product.get("undertone") == profile.get("undertone"):
            score += 25
            reasons.append("undertone match")
        else:
            reasons.append("undertone differs")

        supported_tones = {tone.strip() for tone in product.get("skin_tones", "").split(",")}
        if profile.get("skin_tone") in supported_tones:
            score += 15
            reasons.append("skin tone range match")

        if product.get("cruelty_free") == "Yes":
            score += 5
            reasons.append("cruelty-free preference friendly")

        return {
            "score": min(score, 100),
            "label": "Excellent" if score >= 85 else "Good" if score >= 70 else "Review",
            "reasons": reasons,
        }
