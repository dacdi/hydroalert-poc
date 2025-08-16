# src/domain/models.py
from dataclasses import dataclass

@dataclass(frozen=True)
class BBox:
    minx: int
    miny: int
    maxx: int
    maxy: int

    def validate(self) -> None:
        if not (self.minx < self.maxx and self.miny < self.maxy):
            raise ValueError(f"Invalid BBox: {self}")

    def to_wms(self) -> str:
        return f"{self.minx},{self.miny},{self.maxx},{self.maxy}"

    def __str__(self) -> str:
        return f"BBox({self.minx}, {self.miny}, {self.maxx}, {self.maxy})"
