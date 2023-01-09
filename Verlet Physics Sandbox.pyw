from time import perf_counter
from math import sqrt
from verlet.constraint import distance
import pygame
import verlet

from tkinter import Tk
temp = Tk()

SCREENWIDTH = temp.winfo_screenwidth()
SCREENHEIGHT = temp.winfo_screenheight()

temp.destroy()
del Tk, temp

FPS = 60

class App:
    def __init__(self):
        self.initializeWindow()
        self.initializeWorld()

        #top = self.world.newNode(SCREENWIDTH / 2, SCREENHEIGHT / 2 - 300, pinned=True)
        #middle = self.world.newNode(SCREENWIDTH / 2, SCREENHEIGHT / 2)
        #bottom = self.world.newNode(SCREENWIDTH / 2, SCREENHEIGHT / 2 + 300, xVel=1000)
        #self.world.newConstraint(top, middle, stiffness=1)
        #self.world.newConstraint(middle, bottom, stiffness=1)

        ul = self.world.newNode(100, 100)
        ur = self.world.newNode(300, 100)
        bl = self.world.newNode(100, 300)
        br = self.world.newNode(300, 300)
        self.world.newConstraint(ul, ur)
        self.world.newConstraint(ur, br)
        self.world.newConstraint(br, bl)
        self.world.newConstraint(bl, ul)
        self.world.newConstraint(ur, bl)
        self.world.newConstraint(ul, br)

        while self.running:
            self.frame()

        pygame.quit()

    def initializeWorld(self):
        self.mousePressed = False
        self.mouseX, self.mouseY = None, None
        self.clickX, self.clickY = None, None
        self.clickedNode = None
        self.selectedNodes = []
        self.showDebugText = False
        self.visualizeForces = True
        self.renderNodes = True
        self.renderConstraints = True
        self.running = True
        self.playing = True
        self.airFriction = 0
        self.constraintIterations = 1

        # Each pixel is equivalent to a foot (9.8 meters -> 32.1522 feet)
        self.world = verlet.World((0, 32.1522), 1 - self.airFriction, self.boundary, 1 / FPS)

    def initializeWindow(self):
        pygame.init()
        pygame.display.set_caption('2D Verlet Physics Sandbox')

        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
        self.font = pygame.font.SysFont('Consolas', 15)
        self.clock = pygame.time.Clock()

    def boundary(self, node):
        x, y = node.x, node.y

        if x < node.radius:
            xVel = node.oldX - node.x
            node.x = node.radius
        if y < node.radius:
            yVel = node.oldY - node.y
            node.y = node.radius
        if x > SCREENWIDTH - node.radius:
            xVel = node.x - node.oldX
            node.x = SCREENWIDTH - node.radius
        if y > SCREENHEIGHT - node.radius:
            yVel = node.y - node.oldY
            node.y = SCREENHEIGHT - node.radius
    
    def handleKeys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mousePressed = True
                self.clickX, self.clickY = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mousePressed = False
                self.clickedNode = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.playing = not self.playing
                elif event.key == pygame.K_d:
                    self.showDebugText = not self.showDebugText

    def drawText(self, text, x, y):
        textSurface = self.font.render(text, True, (50, 255, 100))
        textRect = textSurface.get_rect()
        textRect.topleft = x, y
        self.screen.blit(textSurface, textRect)

    def drawDebugText(self, t1, t2, t3):
        uncappedTime = round(t3 - t1, 5)
        physicsTime = round(t2 - t1, 5)
        renderingTime = round(t3 - t2, 5)
        physicsPercentage = round(physicsTime / uncappedTime * 100, 1)
        renderingPercentage = round(renderingTime / uncappedTime * 100, 1)
        squared = u'\u00b2'
        gravityX = f'{str(self.world.gravityX)} u/sec{squared}' if self.world.gravityX else 'None'
        gravityY = f'{str(self.world.gravityY)} u/sec{squared}' if self.world.gravityY else 'None'

        text1 = f'{"Playing" if self.playing else "Paused"} | FPS: {self.clock.get_fps():.1f}/{FPS} ({round(1 / uncappedTime)})'
        text2 = f'Physics: {str(physicsTime).ljust(9)} ({physicsPercentage}%)'
        text3 = f'  Nodes:       {self.world.countNodes()}'
        text4 = f'  Constraints: {self.world.countConstraints()}'
        text5 = f'Rendering: {str(renderingTime).ljust(7)} ({round(renderingTime / self.world.timeStep * 100)}%)'
        text6 = f'Gravity: ({gravityX}, {gravityY})'
        text7 = f'Aerial drag: {self.airFriction * 100}%'
        text8 = f'Constraint iterations: {self.constraintIterations}'

        self.drawText(text1, 15, 15)
        self.drawText(text2, 15, 40)
        self.drawText(text3, 15, 60)
        self.drawText(text4, 15, 80)
        self.drawText(text5, 15, 100)
        self.drawText(text6, 15, 125)
        self.drawText(text7, 15, 145)
        self.drawText(text8, 15, 165)

    def render(self):
        self.screen.fill((10, 25, 50))

        if self.renderConstraints:
            for constraint in self.world.getConstraints():
                x1, y1 = constraint.startNode.x, constraint.startNode.y
                x2, y2 = constraint.endNode.x, constraint.endNode.y
                actualDistance = distance(x1, y1, x2, y2)
                
                color = [255, 255, 255]

                if self.visualizeForces:
                    if actualDistance > constraint.length and not constraint.allowTension:
                        amount = (actualDistance - constraint.length) / actualDistance * 255 if actualDistance else 0
                        color[1] -= amount
                        color[2] -= amount
                        color[1] = max(color[1], 0)
                        color[2] = max(color[2], 0)
                    if actualDistance < constraint.length and not constraint.allowCompression:
                        amount = (constraint.length - actualDistance) / actualDistance * 255 if actualDistance else 0
                        color[0] -= amount
                        color[1] -= amount
                        color[0] = max(color[0], 0)
                        color[1] = max(color[1], 0)
                    
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width=3)

        if self.renderNodes:
            for node in self.world.getNodes():
                pygame.draw.circle(self.screen, (255, 255, 255), (node.x, node.y), node.radius)

        self.handleHighlighting()

    def frame(self):
        t1 = perf_counter()

        self.mouseX, self.mouseY = pygame.mouse.get_pos()
        self.handleDragging()
        if self.playing:
            self.world.update(exclusions=((self.clickedNode,), ()), constraintIterations=self.constraintIterations)

        t2 = perf_counter()

        self.render()

        t3 = perf_counter()
        self.clock.tick(FPS)

        if self.showDebugText:
            self.drawDebugText(t1, t2, t3)

        pygame.display.flip()
        self.handleKeys()

    def handleDragging(self):
        if not self.clickedNode:
            if self.mousePressed:
                closestNode = self.getClosestNode(self.clickX, self.clickY)
                if closestNode:
                    self.clickedNode = closestNode
        
        if self.clickedNode:
            self.clickedNode.oldX, self.clickedNode.oldY = self.clickedNode.x, self.clickedNode.y
            self.clickedNode.x, self.clickedNode.y = self.mouseX, self.mouseY

    def handleHighlighting(self):
        if self.clickedNode:
            pygame.draw.circle(self.screen, (150, 150, 150), (self.clickedNode.x, self.clickedNode.y), self.clickedNode.radius + 8, width=3)
        else:
            closestNode = self.getClosestNode(self.mouseX, self.mouseY)
            if closestNode:
                pygame.draw.circle(self.screen, (70, 70, 70), (closestNode.x, closestNode.y), closestNode.radius + 8, width=3)

    def getClosestNode(self, x, y):
        nodesCloseToPoint = []
        for node in self.world.getNodes():
            distanceToNode = distance(x, y, node.x, node.y)
            if distanceToNode <= 40:
                nodesCloseToPoint.append(node)

        if nodesCloseToPoint:
            closestNode = nodesCloseToPoint[0]
            for node in nodesCloseToPoint:
                distanceToNode = distance(x, y, node.x, node.y)
                if distanceToNode <= distance(x, y, closestNode.x, closestNode.y):
                    closestNode = node
        else:
            return None

        return closestNode

if __name__ == '__main__':
    App()
