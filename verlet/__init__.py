from .node import Node
from .constraint import Constraint, distance
from types import MethodType
from random import sample

class World:
    def __init__(self, gravity: tuple[int | float, int | float], airFriction: float, boundaryFunction: MethodType, timeStep: float):
        '''
        Initializes a world will contain nodes and constraints.

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

    def newNode(self, x: int | float, y: int | float, xVel: int | float=0, yVel: int | float=0, pinned: bool=False, radius: int | float=5) -> int:
        '''
        Creates a new node object with the given parameters.
        Returns the ID of the node (for passing to newConstraint, deleteNode, or configureNode).

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

    def newConstraint(self, startNode: int, endNode: int, length: None | int | float=None, stiffness: float=0.3, allowCompression: bool=False, allowTension: bool=False) -> int:
        '''
        Creates a new constraint object with the given endPoints and parameters.
        Returns the ID of the constraint (for deleteConstraint or configureConstraint).

        Parameters:
            startNode (integer)             An ID returned by newNode after creating a node*
            endNode (integer)               Ditto*
            length (None/integer/float)     The target length of the constraint
                - If length is None, it will be automatically set to the distance between startPoint and endPoint
            stiffness (float)               The stiffness scalar of the constraint (higher = stiffer)
                - Must be between 0 and 1
                - Defaults to 0.5 (50%)
            allowCompression (boolean)      Whether or not the constraint is allowed to be shorter than its desired distance
            allowTension (boolean)          Whether or not the constraint is allowed to be longer than its desired distance
            
            * Will raise an exception if either startPoint or endPoint were deleted
        '''
        startNode = self.getNodeObject(startNode)
        endNode = self.getNodeObject(endNode)

        if not length:
            x1, y1 = startNode.x, startNode.y
            x2, y2 = endNode.x, endNode.y

            length = distance(x1, y1, x2, y2)

        if startNode and endNode:
            self.constraints.append(Constraint(self, startNode, endNode, length, stiffness, allowCompression, allowTension))
            
            return len(self.constraints) - 1
        else:
            raise ValueError('One of the nodes specified has been deleted or is invalid')

    def countNodes(self) -> int:
        '''
        Returns how many nodes exist in the world.
        '''
        return sum(map(bool, self.nodes))

    def countConstraints(self) -> int:
        '''
        Returns how many constraints exist in the world.
        '''
        return sum(map(bool, self.constraints))

    def getNodeObject(self, ID: int) -> None | Node:
        '''
        Returns the node object given its ID.
        Will return None if the node was deleted.

        Parameters:
            ID (integer)                    The ID of the node to retrieve, returned from newNode
        '''
        return self.nodes[ID]

    def getConstraintObject(self, ID: int) -> None | Node:
        '''
        Returns the constraint object given its ID.
        Will return None if the constraint was deleted.

        Parameters:
            ID (integer)                    The ID of the constraint to retrieve, returned from newConstraint
        '''
        return self.constraints[ID]

    def getNodes(self) -> filter:
        '''
        Returns all existing nodes in the world as an iterator.
        '''
        return filter(bool, self.nodes)

    def getConstraints(self) -> filter:
        '''
        Returns all existing constraints in the world as an iterator.
        '''
        return filter(bool, self.constraints)

    def deleteNode(self, ID: int):
        '''
        Deletes a node given its ID.
        Also deletes all constraints connected to the node.

        Parameters:
            ID (integer)                    The ID of the node to be deleted, returned from newNode
        '''
        for constraintID, constraint in self.constraints:
            if constraint and self.getNodeObject(ID) in (constraint.startNode, constraint.endNode):
                self.deleteConstraint(constraintID)

        self.nodes[ID] = None

    def deleteConstraint(self, ID: int, deleteConnectedNodes: bool=False):
        '''
        Deletes a constraint given its ID.

        Parameters:
            ID (integer)                    The ID of the constraint to be deleted, returned from newConstraint
            deleteConnectedNodes (boolean)  Whether or not to delete all nodes the constraint was connected to
                - Disabled by default
        '''
        if deleteConnectedNodes:
            constraint = self.getConstraintObject(ID)

            for nodeID, node in enumerate(self.getNodes()):
                if node and node in (constraint.startPoint, constraint.endPoint):
                    self.deleteNode(nodeID)

        self.constraints[ID] = None

    def setNodeVelocity(self, ID: int, xVel: int | float, yVel: int | float):
        '''
        Sets the velocity, in units/second, of a node.

        Parameters:
            ID (integer)                    The ID of the node to change, returned from newNode
            xVel (integer/float)            The horizontal velocity, in units/second
            yVel (integer/float)            The vertical velocity, in units/second
        '''
        node = self.getNodeObject(ID)

        if node:
            node.oldX = node.x - xVel * self.timeStep
            node.oldY = node.y - yVel * self.timeStep

    def addNodeVelocity(self, ID: int, xVel: int | float, yVel: int | float):
        '''
        Changes the velocity, in units/second, of a node.

        Parameters:
            ID (integer)                    The ID of the node to change, returned from newNode
            xVel (integer/float)            The horizontal velocity, in units/second, to be added
            yVel (integer/float)            The vertical velocity, in units/second, to be added
        '''
        node = self.getNodeObject(ID)

        if node:
            node.oldX -= xVel * self.timeStep
            node.oldY -= yVel * self.timeStep

    def configureNode(self, ID: int, **kwargs):
        '''
        Directly changes any parameter of a node.

        Parameters:
            ID (integer)                    The ID of the node to change, returned from newNode
            See newNode for more options
        '''
        node = self.getNodeObject(ID)

        if node:
            for attribute in kwargs:
                if attribute == 'xVel':
                    node.oldX = node.x - kwargs['xVel'] * self.timeStep

                elif attribute == 'yVel':
                    node.oldY = node.y - kwargs['yVel'] * self.timeStep

                else:
                    setattr(node, attribute, kwargs[attribute])

    def configureConstraint(self, ID: int, **kwargs):
        '''
        Directly changes any parameter of a constraint.

        Parameters:
            ID (integer)                    The ID of the constraint to change, returned from newConstraint
            See newConstraint for more options *

            Start and end nodes should be set to the Node objects here, not their IDs
        '''
        constraint = self.getConstraintObject(ID)

        if constraint:
            for attribute in kwargs:
                setattr(constraint, attribute, kwargs[attribute])

    def update(self, exclusions: tuple=((), ()), updateRandomly: tuple=(False, False), constraintIterations: int=1):
        '''
        Updates all nodes and constraints in the world according to the world's time step, once.

        Parameters:
            exclusions (2D tuple)           A 2D tuple representing which nodes and constraints to not update
                - The first subtuple contains which nodes to not update
                - The second subtuple contains which constraints to not update
                - These are node and constraint objects, not IDs
            updateRandomly (tuple)          A tuple representing whether or not to randomly update
                - The first item is whether or not to update nodes randomly
                - The second item is whether or not to update constraints randomly
            constraintIterations (integer)  How many times to update the constraints
                - Once by default
        '''
        nodeIterator = sample(tuple(self.getNodes()), self.countNodes()) if updateRandomly[0] else self.getNodes()
        constraintIterator = sample(tuple(self.getConstraints()), self.countConstraints()) if updateRandomly[1] else self.getConstraints()

        for node in nodeIterator:
            if exclusions[0]:
                if node not in exclusions[0]:
                    node.update()

            else:
                node.update()

        for _ in range(constraintIterations):
            for constraint in constraintIterator:
                if exclusions[1]:
                    if constraint not in exclusions[1]:
                        constraint.update()

                else:
                    constraint.update()
