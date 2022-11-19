class Node:
    def __init__(self, world, x, y, velX=0.0, velY=0.0,
                 pinned=False, radius=5.0):
        self.world = world

        self.x, self.y = x, y
        self.velX, self.velY = velX, velY
        self.oldX = self.x - self.velX
        self.oldY = self.y + self.velY

        self.pinned = pinned
        self.radius = radius

    def update(self):
        if not self.pinned:
            self.physicsStep()
            self.applyBoundaries()

    def physicsStep(self):
        self.velX = (self.x - self.oldX) * self.world.airFriction
        self.velY = (self.y - self.oldY) * self.world.airFriction

        self.oldX, self.oldY = self.x, self.y
        self.x += self.velX - self.world.gravityX * self.world.timeStep
        self.y += self.velY - self.world.gravityY * self.world.timeStep

    def applyBoundaries(self):
        self.world.boundaryFunction(self)
