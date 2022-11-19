from math import sqrt

def distance(point1, point2):
    return sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)

class Constraint:
    def __init__(self, world, startPoint, endPoint, length=None, stiffness=0.3):
        self.world = world

        self.startPoint = startPoint
        self.endPoint = endPoint
        self.calculateLength()
        self.stiffness = stiffness

    def calculateLength(self, length=None):
        self.length = distance(self.startPoint, self.endPoint) if not length else length

    def update(self):
        diffX = self.startPoint.x - self.endPoint.x
        diffY = self.startPoint.y - self.endPoint.y
        dist = distance(self.startPoint, self.endPoint)

        difference = 0
        if dist > 0:
            difference = (self.length - dist) / dist

        translateX = diffX * (difference / 2 * self.stiffness)
        translateY = diffY * (difference / 2 * self.stiffness)

        if not self.startPoint.pinned:
            self.startPoint.x += translateX
            self.startPoint.y += translateY
            self.startPoint.applyBoundaries()

        if not self.endPoint.pinned:
            self.endPoint.x -= translateX
            self.endPoint.y -= translateY
            self.endPoint.applyBoundaries()
