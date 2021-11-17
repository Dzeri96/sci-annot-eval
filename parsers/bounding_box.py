class BoundingBox():
    def __init__(self, type: str,  x: float, y: float, height: float, width: float, parent: str) -> None:
        self.type = type
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.parent = parent
    
    def __str__(self) -> str:
        return f'{{type: {self.type}, x:{self.x}, y:{self.y}, width: {self.width}, height: {self.height}, parent: {self.parent}}}'