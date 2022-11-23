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
        x, y = self.x, self.y
        oldX, oldY = self.oldX, self.oldY
        self.oldX, self.oldY = x, y
        airFriction, timeStep = self.world.airFriction, self.world.timeStep

        self.x += (x - oldX) * airFriction - self.world.gravityX * timeStep
        self.y += (y - oldY) * airFriction - self.world.gravityY * timeStep

    def applyBoundaries(self):
        self.world.boundaryFunction(self)
