from typing import TypedDict

class Annotation(TypedDict):
    type: str
    body: list[dict]
    target: dict
    id: str