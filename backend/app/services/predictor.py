import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Prediction:
    label: str
    latitude: float
    longitude: float
    confidence: float
    bbox_left: float
    bbox_top: float
    bbox_width: float
    bbox_height: float


class Predictor:
    """Deterministic stub predictor based on file hash."""

    def predict(self, image_path: Path) -> List[Prediction]:
        data = image_path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        seed = int(digest[:16], 16)
        latitude = (seed % 1800000) / 10000 - 90
        longitude = (seed // 1800000 % 3600000) / 10000 - 180
        confidence = ((seed % 1000) / 1000) * 0.5 + 0.5
        bbox_seed = int(digest[16:24], 16)
        bbox_left = (bbox_seed % 6000) / 10000
        bbox_top = ((bbox_seed // 6000) % 6000) / 10000
        bbox_width = 0.3 + ((bbox_seed % 5000) / 20000)
        bbox_height = 0.3 + (((bbox_seed // 5000) % 5000) / 20000)
        prediction = Prediction(
            label="building",
            latitude=latitude,
            longitude=longitude,
            confidence=min(confidence, 0.99),
            bbox_left=min(bbox_left, 0.9),
            bbox_top=min(bbox_top, 0.9),
            bbox_width=min(bbox_width, 1.0),
            bbox_height=min(bbox_height, 1.0),
        )
        return [prediction]
