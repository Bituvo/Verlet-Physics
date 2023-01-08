from math import sqrt

def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class Constraint:
    def __init__(self, world, startNode, endNode, length, stiffness, allowCompression, allowTension):
        self.world = world

        self.startNode = startNode
        self.endNode = endNode
        self.length, self.stiffness = length, stiffness

        self.allowCompression = allowCompression
        self.allowTension = allowTension

    def realDistance(self):
        x1, y1 = self.startNode.x, self.startNode.y
        x2, y2 = self.endNode.x, self.endNode.y
        
        return distance(x1, y1, x2, y2)

    def constrain(self, distance=None):
        distance = distance or self.realDistance()

        difference = (self.length - distance) / distance if distance > 0 else 0
        translateX = (self.startNode.x - self.endNode.x) * (difference / 2 * self.stiffness)
        translateY = (self.startNode.y - self.endNode.y) * (difference / 2 * self.stiffness)

        if not self.startNode.pinned:
            self.startNode.x += translateX
            self.startNode.y += translateY

            self.world.boundaryFunction(self.startNode)

        if not self.endNode.pinned:
            self.endNode.x -= translateX
            self.endNode.y -= translateY

            self.world.boundaryFunction(self.endNode)

    def update(self):
        if not self.allowCompression and not self.allowTension:
            self.constrain()

        else:
            distance = self.realDistance()

            if self.allowCompression and distance > self.length:
                self.constrain(distance)

            if self.allowTension and distance < self.length:
                self.constrain(distance)
