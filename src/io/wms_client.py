from dataclasses import dataclass
from typing import Dict
import requests
from requests.adapters import HTTPAdapter, Retry

@dataclass(frozen=True)
class BBox:
    minx: int
    miny: int
    maxx: int
    maxy: int
    def to_wms(self) -> str:
        return f"{self.minx},{self.miny},{self.maxx},{self.maxy}"

def build_wms_params(layer: str, bbox: BBox, width: int, height: int) -> Dict[str, str]:
    return {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": layer,
        "bbox": bbox.to_wms(),
        "width": width,
        "height": height,
        "crs": "EPSG:25832",
        "format": "image/png",
    }

_session = requests.Session()
_session.mount(
    "https://",
    HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])),
)

def fetch_wms_png(base_url: str, params: Dict[str, str], timeout: float = 15.0) -> bytes:
    resp = _session.get(base_url, params=params, timeout=timeout)
    resp.raise_for_status()
    ctype = resp.headers.get("Content-Type", "")
    if "image/png" not in ctype:
        raise ValueError(f"Unexpected content type: {ctype}")
    return resp.content
