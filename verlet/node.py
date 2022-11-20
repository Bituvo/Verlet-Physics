class Node:
    def __init__(self, world, x, y, xVel=0.0, yVel=0.0,
                 pinned=False, radius=5.0):
        self.world = world

        self.x, self.y = x, y
        self.oldX = self.x - xVel
        self.oldY = self.y + yVel

        self.pinned = pinned
        self.radius = radius

    def update(self):
        if not self.pinned:
            self.physicsStep()
            self.applyBoundaries()

    def physicsStep(self):
        xVel = (self.x - self.oldX) * self.world.airFriction
        yVel = (self.y - self.oldY) * self.world.airFriction

        self.oldX, self.oldY = self.x, self.y
        self.x += xVel - self.world.gravityX * self.world.timeStep
        self.y += yVel - self.world.gravityY * self.world.timeStep

    def applyBoundaries(self):
        self.world.boundaryFunction(self)
