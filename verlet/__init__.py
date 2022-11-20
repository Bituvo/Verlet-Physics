from .node import Node
from .constraint import Constraint
from types import MethodType
from typing import Union
from random import sample

class World:
    def __init__(self, gravity: tuple, airFriction: float, boundaryFunction: MethodType, timeStep: float):
        '''
        Initializes the world that contains nodes and constraints

        Parameters:
            gravity (tuple)                 A tuple containing horizontal and vertical gravity in the form of units/second squared
            airFriction (float)             The air friction/drag coefficient
            boundaryFunction (function)     A function that takes a Node object as input and enforces boundaries with its position
            timeStep (float)                The target delta time for the simulation, e.g. 1 / 60 for 60 FPS target
        '''
        self.gravityX, self.gravityY = gravity
        self.airFriction = airFriction
        self.boundaryFunction = boundaryFunction
        self.timeStep = timeStep

        self.nodes, self.constraints = [], []

    def newNode(self, x: Union[int, float], y: Union[int, float], xVel: Union[int, float]=0, yVel: Union[int, float]=0, pinned: bool=False, radius: Union[int, float]=5) -> int:
        '''
        Creates a new node object with the given parameters
        Returns the ID of the node (for passing to newConstraint, deleting or changing)

        Parameters:
            x (integer/float)               The X position of the node to be created
            y (integer/float)               The Y position of the node to be created
            velX (integer/float)            The X velocity of the node to be created*
            velY (integer/float)            The Y velocity of the node to be created*
            pinned (boolean)                Whether or not the node is restricted from changing position
                - Unpinned by default
            radius (integer/float)          The radius of the node in units
                - Radius is 5 units by default

            * Measured in units/second, no velocity by default
        '''
        self.nodes.append(Node(self, x, y, xVel, yVel, pinned, radius))
        return len(self.nodes) - 1

    def newConstraint(self, startPoint: int, endPoint: int, length: Union[None, int, float]=None, stiffness: float=0.5) -> int:
        '''
        Creates a new constraint object with the given endPoints and parameters
        Returns the ID of the constraint (for deleting or changing)

        Parameters:
            startPoint (integer)            An ID returned by newNode after creating a node*
            endPoint (integer)              Ditto*
            length (None/integer/float)     The target length of the constraint
                - If length is None, it will be automatically set to the distance between startPoint and endPoint
            stiffness (float)               The stiffness scalar of the constraint (higher = stiffer)
                - Must be between 0 and 1
                - Defaults to 0.5 (50%)
            
            * Will raise an exception if either startPoint or endPoint were deleted
        '''
        if self.nodes[startPoint] and self.nodes[endPoint]:
            self.constraints.append(Constraint(self, self.nodes[startPoint], self.nodes[endPoint], length, stiffness))
            return len(self.constraints) - 1
        else:
            raise ValueError('One of the nodes specified has been deleted')

    def countNodes(self) -> int:
        '''
        Returns how many nodes exist in the world
        '''
        return sum(map(lambda item: bool(item), self.nodes))

    def countConstraints(self) -> int:
        '''
        Returns how many constraints exist in the world
        '''
        return sum(map(lambda item: bool(item), self.constraints))

    def getNodeObject(self, ID: int) -> Union[None, Node]:
        '''
        Returns the node object given its ID
        Will return None if the node was deleted

        Parameters:
            ID (integer)                    The ID of the node to retrieve
        '''
        return self.nodes[ID]

    def getConstraintObject(self, ID: int) -> Union[None, Node]:
        '''
        Returns the constraint object given its ID
        Will return None if the constraint was deleted

        Parameters:
            ID (integer)                    The ID of the constraint to retrieve
        '''
        return self.constraints[ID]

    def getNodes(self) -> tuple:
        '''
        Returns all existing nodes in the world
        '''
        return tuple([node for node in self.nodes if node])

    def getConstraints(self) -> tuple:
        '''
        Returns all existing constraints in the world
        '''
        return tuple([constraint for constraint in self.constraints if constraint])

    def deleteNode(self, ID: int):
        '''
        Deletes a node given its ID
        Also deletes all constraints connected to the node

        Parameters:
            ID (integer)                    The ID of the node to be deleted, returned from newNode
        '''
        for ID, constraint in enumerate(self.getConstraints()):
            if self.nodes[ID] in (constraint.startPoint, constraint.endPoint):
                self.deleteConstraint(ID)

        self.nodes[ID] = None

    def deleteConstraint(self, ID: int, deleteConnectedNodes: bool=False):
        '''
        Deletes a constraint given its ID

        Parameters:
            ID (integer)                    The ID of the constraint to be deleted, returned from newConstraint
            deleteConnectedNodes (boolean)  Whether or not to delete all nodes the constraint was connected to
                - Disabled by default
        '''
        if deleteConnectedNodes:
            constraint = self.getConstraintObject(ID)

            for ID, node in enumerate(self.getNodes()):
                if node in [constraint.startPoint, constraint.endPoint]: # type: ignore
                    self.deleteNode(ID)

        self.constraints[ID] = None

    def update(self, updateRandomly: tuple=(False, False), constraintIterations: int=1):
        '''
        Updates all nodes and constraints in the world once

        Parameters:
            updateRandomly (tuple)          A tuple representing whether or not to randomly update
                - The first item is whether or not to update nodes randomly
                - The second item is whether or not to update constraints randomly
            constraintIterations (integer)  How many times to update the constraints
                - Once by default
        '''
        nodeIterator = sample(self.getNodes(), self.countNodes()) if updateRandomly[0] else self.getNodes()
        constraintIterator = sample(self.getConstraints(), self.countConstraints()) if updateRandomly[1] else self.getConstraints()

        for node in nodeIterator: node.update()
        for iteration in range(constraintIterations):
            for constraint in constraintIterator:
                constraint.update()
