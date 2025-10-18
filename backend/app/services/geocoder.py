import hashlib
from dataclasses import dataclass

from ..core.config import settings


@dataclass
class GeoPoint:
    latitude: float
    longitude: float


class Geocoder:
    """Offline-first geocoder stub."""

    def reverse(self, latitude: float, longitude: float) -> str:
        return f"{settings.offline_geocoder_prefix}: {latitude:.5f}, {longitude:.5f} ({settings.offline_geocoder_city})"

    def forward(self, query: str) -> GeoPoint:
        digest = hashlib.sha1(query.encode("utf-8")).hexdigest()
        seed = int(digest[:16], 16)
        latitude = (seed % 1800000) / 10000 - 90
        longitude = (seed // 1800000 % 3600000) / 10000 - 180
        return GeoPoint(latitude=latitude, longitude=longitude)


geocoder = Geocoder()
