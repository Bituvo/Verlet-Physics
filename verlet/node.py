class Node:
    def __init__(self, world, x, y, xVel, yVel, pinned, radius):
        self.world = world

        self.x, self.y = x, y
        self.oldX = x - xVel * self.world.timeStep
        self.oldY = y - yVel * self.world.timeStep

        self.pinned = pinned
        self.radius = radius

    def update(self):
        if not self.pinned:
            self.physicsStep()
            self.world.boundaryFunction(self)

    def physicsStep(self):
        x, y = self.x, self.y
        oldX, oldY = self.oldX, self.oldY
        self.oldX, self.oldY = x, y

        airFriction, timeStep = self.world.airFriction, self.world.timeStep
        self.x += (x - oldX) * airFriction + self.world.gravityX * timeStep
        self.y += (y - oldY) * airFriction + self.world.gravityY * timeStep
