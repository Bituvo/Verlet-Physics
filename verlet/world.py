class World:
    def __init__(self, width, height, gravity, airFriction, boundaryFunction):
        self.width, self.height = width, height
        self.gravityX, self.gravityY = gravity
        self.airFriction = airFriction
        self.boundaryFunction = boundaryFunction
