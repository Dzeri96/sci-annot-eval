from typing import TypedDict, Literal

class AnnotationBody(TypedDict):
    type: Literal["TextualBody"]
    purpose: Literal["img-cap-enum", "parent"]
    value: str

Annotation = TypedDict(
    "Annotation", {
        "type": Literal["Annotation"],
        "body": list[AnnotationBody],
        "target": dict,
        "id": str,
        "@context": Literal["http://www.w3.org/ns/anno.jsonld"]
    }
)

class SciAnnotOutput(TypedDict):
    canvasHeight: int
    canvasWidth: int
    annotations: list[Annotation]

