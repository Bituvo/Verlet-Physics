from time import process_time
from tkinter import ttk
import tkinter as tk
import verlet
from verlet.constraint import distance

from random import shuffle

class App:
    # INITIALIZATION

    def __init__(self):
        # Create fullscreen window
        self.master = tk.Tk()
        self.master.title('Verlet Physics Sandbox')
        self.master.wm_attributes('-fullscreen', True)
        screenWidth, screenHeight = self.master.winfo_screenwidth() - 500, self.master.winfo_screenheight()

        self.createCanvas(screenWidth, screenHeight)
        self.initializeVariables(screenWidth, screenHeight)
        self.createGUI()
        self.createContextMenu()
        self.setBindings()

        self.createCloth(21, 15, 50)

        self.frame()
        self.master.mainloop()

    def createCloth(self, width, height, size):
        x1 = (int(self.canvas['width']) / 2) - (width * size / 2)
        y1 = (int(self.canvas['height']) / 2) - (height * size / 2)

        for y in range(0, height * size, size):
            for x in range(0, width * size, size):
                self.world.newNode(x + x1, y + y1)

        for ID, node in enumerate(self.world.getNodes()):
            if node.y == y1:
                if not ((node.x - x1) / size) % 2:
                    node.pinned = True
            else:
                self.world.newConstraint(ID, ID - width, stiffness=1)

            if node.x > x1 and node.x < x1 + width * size:
                if node.y == y1:
                    self.world.newConstraint(ID, ID - 1, stiffness=0.5)
                else:
                    self.world.newConstraint(ID, ID - 1, stiffness=1)

        shuffle(self.world.nodes)

    def createCanvas(self, screenWidth, screenHeight):
        self.canvas = tk.Canvas(self.master, width=screenWidth,
                                height=screenHeight, bg='white', highlightthickness=0)
        self.canvas.pack(side='left')

    def initializeVariables(self, screenWidth, screenHeight):
        self.playing = False
        self.mode = 'node'
        self.selectedStartNode, self.selectedEndNode = None, None
        self.world = verlet.World((0, -32), 0.99, self.boundary, 1 / 60) # type: ignore
        setattr(self.world, 'width', screenWidth)
        setattr(self.world, 'height', screenHeight)
        self.nodeSelectionCircle = None
        self.selectionBox, self.selectedNode = None, None
        self.selectedNodeWasPinned = False
        self.selX1, self.selY1 = None, None
        self.selectedNodes = []
        self.nodeDragSmoothing = 4
        self.contextMenuOpen = False

    def createContextMenu(self):
        self.contextMenu = tk.Menu(self.canvas, font=('', 13), tearoff=False, borderwidth=5)
        self.contextMenu.add_command( label='Select all', command=self.selectAll, accelerator='Ctrl-A')
        self.contextMenu.add_separator()
        self.contextMenu.add_command(label='Delete selection', command=self.deleteSelection, accelerator='Del')
        self.contextMenu.add_command(label='Delete attached constraints', command=self.deleteSelectedAttachedConstraints, accelerator='Ctrl-Del')
        self.contextMenu.add_command(label='Delete all', command=self.deleteAll, accelerator='Shift-Del')

    def setBindings(self):
        self.canvas.bind('<Button-1>', self.mouseDown)
        self.canvas.bind('<Motion>', self.mouseMotion)
        self.canvas.bind('<ButtonRelease-1>', self.mouseUp)
        self.canvas.bind('<Button-3>', self.showContextMenu)
        self.master.bind('<Control-a>', self.selectAll)
        self.master.bind('<Delete>', self.deleteSelection)
        self.master.bind('<Control-Delete>', self.deleteSelectedAttachedConstraints)
        self.master.bind('<Shift-Delete>', self.deleteAll)
        self.master.bind('<space>', self.togglePlay)

    # OPTIONS INTERFACE

    def createGUI(self):
        style = ttk.Style()
        style.configure('LargeText.TButton', font=('Segoe UI', 15))

        self.guiFrame = tk.Frame(self.master)
        self.guiFrame.pack_propagate(False)

        modeFrame = tk.Frame(self.guiFrame)
        ttk.Button(modeFrame, text='Node', command=self.nodeMode, style='LargeText.TButton').pack(side='left', fill='x', expand=True, ipady=50, padx=10)
        ttk.Button(modeFrame, text='Constraint', command=self.constraintMode, style='LargeText.TButton').pack(side='left', fill='x', expand=True, ipady=50, padx=10)
        ttk.Button(modeFrame, text='Select', command=self.selectMode, style='LargeText.TButton').pack(side='left', fill='x', expand=True, ipady=50, padx=10)
        modeFrame.pack(side='top', fill='y', padx=10, pady=20)

        self.createNodeOptions(self.guiFrame)
        self.createConstraintOptions(self.guiFrame)

        self.guiFrame.pack(side='left', fill='both', expand=True)

    def createNodeOptions(self, master):
        nodeOptionsFrame = tk.LabelFrame(master, text='Node options', relief='flat')

        self.newNodeVelX = tk.StringVar()
        self.newNodeVelY = tk.StringVar()
        self.newNodeRadius = tk.StringVar()
        self.newNodePinned = tk.IntVar()

        velSpinboxValidateCommand = nodeOptionsFrame.register(self.velSpinboxValidate), '%P'
        radSpinboxValidateCommand = nodeOptionsFrame.register(self.radSpinboxValidate), '%P'

        tk.Label(nodeOptionsFrame, text='X Velocity').pack(side='left')
        ttk.Spinbox(nodeOptionsFrame, from_=-40, to=40, width=1, textvariable=self.newNodeVelX, validate='key', validatecommand=velSpinboxValidateCommand).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Label(nodeOptionsFrame, text='Y Velocity').pack(side='left')
        ttk.Spinbox(nodeOptionsFrame, from_=-40, to=40, width=1, textvariable=self.newNodeVelY, validate='key', validatecommand=velSpinboxValidateCommand).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Label(nodeOptionsFrame, text='Radius').pack(side='left')
        ttk.Spinbox(nodeOptionsFrame, from_=1, to=30, width=1, textvariable=self.newNodeRadius, validate='key', validatecommand=radSpinboxValidateCommand).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Label(nodeOptionsFrame, text='Pinned').pack(side='left')
        ttk.Checkbutton(nodeOptionsFrame, variable=self.newNodePinned).pack(side='left', fill='x', expand=False)
        nodeApplyButton = ttk.Button(nodeOptionsFrame, text='Apply to selection', command=self.applyNodeOptions)
        nodeApplyButton.pack(side='left', fill='x', expand=False)

        nodeOptionsFrame.pack(fill='x', padx=10, pady=(0, 20), ipady=10)

    def createConstraintOptions(self, master):
        constraintOptionsFrame = tk.LabelFrame(master, text='Constraint options', relief='flat')

        self.newConstraintLength = tk.StringVar()
        self.newConstraintStiffness = tk.StringVar()

        lenSpinboxValidateCommand = constraintOptionsFrame.register(self.lenSpinboxValidate), '%P'
        stiSpinboxValidateCommand = constraintOptionsFrame.register(self.stiSpinboxValidate), '%P'

        tk.Label(constraintOptionsFrame, text='Length (pixels)').pack(side='left')
        ttk.Spinbox(constraintOptionsFrame, from_=1, to=1500, width=1, textvariable=self.newConstraintLength, validate='key', validatecommand=lenSpinboxValidateCommand).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Label(constraintOptionsFrame, text='Stiffness (scalar)').pack(side='left')
        ttk.Spinbox(constraintOptionsFrame, from_=0, to=1, increment=0.05, width=1, textvariable=self.newConstraintStiffness, validate='key', validatecommand=stiSpinboxValidateCommand).pack(side='left', fill='x', expand=True, padx=(0, 5))
        constraintApplyButton = ttk.Button(constraintOptionsFrame, text='Apply to selection', command=self.applyConstraintOptions)
        constraintApplyButton.pack(side='left', fill='x', expand=False)

        constraintOptionsFrame.pack(fill='x', padx=10, pady=(0, 20), ipady=10)

    def velSpinboxValidate(self, value): return self.spinboxValidate(value, -40, 40)
    def radSpinboxValidate(self, value): return self.spinboxValidate(value, 1, 30)
    def lenSpinboxValidate(self, value): return self.spinboxValidate(value, 5, 1500)
    def stiSpinboxValidate(self, value): return self.spinboxValidate(value, 0, 1)

    def spinboxValidate(self, value, minimum, maximum):
        if not value or value in ['-', ',']: return True
        try:
            value = float(value)
            return minimum <= value <= maximum
        except ValueError: return False

    def getNodeOptions(self):
        userVelX = self.newNodeVelX.get()
        userVelY = self.newNodeVelY.get()
        userPinned = self.newNodePinned.get()
        userRadius = self.newNodeRadius.get()

        if userVelX in ['-', '.', '']: userVelX = 0
        else: userVelX = float(userVelX)
        if userVelY in ['-', '.', '']: userVelY = 0
        else: userVelY = float(userVelY)
        if userRadius in ['-', '.', '']: userRadius = 5
        else: userRadius = float(userRadius)

        return userVelX, userVelY, bool(userPinned), userRadius

    def getConstraintOptions(self):
        userLength = self.newConstraintLength.get()
        userStiffness = self.newConstraintStiffness.get()

        if userLength in ['-', '.', '']: userLength = None
        else: userLength = float(userLength)
        if userStiffness in ['-', '.', '']: userStiffness = 0.3
        else: userStiffness = float(userStiffness)

        return userLength, userStiffness

    # RENDERING AND PHYSICS

    def frame(self):
        # Update everything and render, try to stick to 60 FPS
        t1 = process_time()
        
        if self.playing:
            self.world.update(constraintIterations=1)

        self.render()
        self.handleNodeSelection()
        self.master.update()

        t2 = process_time()
        if t2 - t1 > 1 / 60:
            self.master.after(0, self.frame)
        else:
            self.master.after(round((1 / 60 - (t2 - t1)) * 1000), self.frame)

    def render(self):
        # Delete all "temporary" (currently drawn nodes and constraints) items and redraw
        self.canvas.delete('temp')
        self.canvas.delete(self.nodeSelectionCircle or 0)

        # Draw all constraints
        for constraint in self.world.getConstraints():
            x1, y1 = constraint.startPoint.x, constraint.startPoint.y
            x2, y2 = constraint.endPoint.x, constraint.endPoint.y

            self.canvas.create_line(
                x1, y1, x2, y2, width=3, fill='#000', tags='temp')

        # Draw all points
        for node in self.world.getNodes():
            x1, y1 = node.x - node.radius, node.y - node.radius
            x2, y2 = node.x + node.radius, node.y + node.radius
            fill = '#555' if node in self.selectedNodes or node == self.selectedNode else '#000'

            point = self.canvas.create_oval(
                x1, y1, x2, y2, outline='', fill=fill, tags='temp')

        # Draw node selection circles and the selection box
        # https://stackoverflow.com/questions/74504174/how-do-i-create-an-object-with-subvalues-without-creating-a-class
        self.drawNodeSelectionCircle(type('point', (), {'x': self.master.winfo_pointerx(), 'y': self.master.winfo_pointery()}))
        self.drawSelectionBox()
        self.canvas.update()

    def boundary(self, node):
        # Boundary function for the world initialization, just a box overlap check
        x, y = node.x, node.y

        if x < node.radius:
            velX = node.oldX - node.x
            node.x = node.radius
            node.oldX = node.x - velX * 0.4
        if y < node.radius:
            velY = node.oldY - node.y
            node.y = node.radius
            node.oldY = node.y - velY * 0.4
        if x > node.world.width - node.radius:
            velX = node.x - node.oldX
            node.x = node.world.width - node.radius
            node.oldX = node.x + velX * 0.4
        if y > node.world.height - node.radius:
            velY = node.y - node.oldY
            node.y = node.world.height - node.radius
            node.oldY = node.y + velY * 0.4
            # Apply ground friction
            velX = (node.x - node.oldX) * 0.8
            node.oldX = node.x - velX

    def findDistance(self, point1, point2):
        if not point2:
            return float('+inf')
        return distance(point1, point2)

    # CONTEXT MENU

    def showContextMenu(self, event):
        closestNode = self.findClosestNode(event)
        if closestNode:
            self.selectedNode = closestNode
            if closestNode.pinned: self.selectedNodeWasPinned = True

        self.contextMenuOpen = True
        self.contextMenu.tk_popup(event.x, event.y, 0)
        self.contextMenuOpen = False

    def selectAll(self, event=None):
        if not self.playing:
            self.selectMode()
            self.selectedNodes = self.world.getNodes()

    def deleteSelection(self, event=None):
        if not self.playing:
            self.deleteSelectedAttachedConstraints()
            newNodes = []

            for node in self.world.getNodes():
                if node not in self.selectedNodes and node != self.selectedNode:
                    newNodes.append(node)

            self.world.nodes = newNodes

    def deleteSelectedAttachedConstraints(self, event=None):
        if not self.playing:
            newConstraints = []

            for constraint in self.world.getConstraints():
                if constraint.startPoint not in self.selectedNodes and constraint.endPoint not in self.selectedNodes:
                    newConstraints.append(constraint)

            self.world.constraints = newConstraints

    def deleteAll(self, event=None):
        if not self.playing:
            self.world.nodes, self.world.constraints, self.selectedNodes = [], [], []
    
    # INTERACTION AND MODES

    def nodeMode(self):
        # Set the drawing mode to 'node' and delete any unfinished constraints
        self.selectedStartNode = None
        self.canvas.delete('preview')
        self.selectedNodes = []
        self.mode = 'node'

    def constraintMode(self):
        # Self explanatory
        self.selectedNodes = []
        self.mode = 'constraint'

    def selectMode(self):
        # Set mode to selection, for dragging and, well, selection
        self.selectedStartNode = None
        self.canvas.delete('preview')
        self.selectedNodes = []
        self.mode = 'select'

    def togglePlay(self, event):
        # Pause or unpause (event can be literally anything, doesn't matter)
        self.selectedNodes = []
        self.playing = not self.playing
        self.canvas.focus_set()

    def findClosestNode(self, point1):
        # Find the closest node to a position that is 30 or less pixels away
        closestNode = None

        for point in self.world.getNodes():
            distance = self.findDistance(point1, point)
            if distance < self.findDistance(point1, closestNode) and distance <= 30:
                closestNode = point

        return closestNode

    # SELECTION

    def handleNodeSelection(self):
        if self.selectedNode and not self.contextMenuOpen:
            x, y = self.selectedNode.x, self.selectedNode.y
            mousePoint = type('point', (), {'x': self.master.winfo_pointerx(), 'y': self.master.winfo_pointery(), 'radius': 0, 'world': self.world})
            self.boundary(mousePoint)
            mouseX, mouseY = mousePoint.x, mousePoint.y # type: ignore

            self.selectedNode.oldX = self.selectedNode.x
            self.selectedNode.oldY = self.selectedNode.y
            if self.playing:
                self.selectedNode.x += (mouseX - x) / self.nodeDragSmoothing
                self.selectedNode.y += (mouseY - y) / self.nodeDragSmoothing
            else:
                self.selectedNode.x, self.selectedNode.y = mouseX, mouseY

            if self.selectedNodes:
                for point in self.selectedNodes:
                    if point != self.selectedNode:
                        point.oldX, point.oldY = point.x, point.y
                        
                        point.x += mouseX - x
                        point.y += mouseY - y

    def drawNodeSelectionCircle(self, event):
        self.canvas.delete(self.nodeSelectionCircle or 0)
        closestNode = self.findClosestNode(event)

        if closestNode:
            x, y, radius = closestNode.x, closestNode.y, closestNode.radius
            x1, y1 = x - radius - 8, y - radius - 8
            x2, y2 = x + radius + 8, y + radius + 8

            self.nodeSelectionCircle = self.canvas.create_oval(
                x1, y1, x2, y2, outline='#555', width=3)

    def drawSelectionBox(self):
        self.canvas.delete(self.selectionBox or 0)
        if self.selX1 and self.selY1:
            self.selectionBox = self.canvas.create_rectangle(
                self.selX1, self.selY1, self.master.winfo_pointerx(), self.master.winfo_pointery(), outline='#0af')
    
    def applyNodeOptions(self):
        userVelX, userVelY, userPinned, userRadius = self.getNodeOptions()

        for node in self.selectedNodes:
            node.oldX = node.x - userVelX
            node.oldY = node.y - userVelY
            node.pinned = userPinned
            node.radius = userRadius

    def applyConstraintOptions(self):
        userLength, userStiffness = self.getConstraintOptions()

        constraints = []
        for node in self.selectedNodes:
            for constraint in self.world.getConstraints():
                if node in [constraint.startPoint, constraint.endPoint]:
                    constraints.append(constraint)

        for constraint in constraints:
            constraint.length = userLength
            constraint.stiffness = userStiffness
            constraint.calculateLength()

    # MOUSE EVENTS

    def mouseDown(self, event):
        # Handle drawing and drag starting
        mouseX, mouseY = event.x, event.y

        if self.mode == 'node':
            # Don't create a new node if another node is too close
            if not self.findClosestNode(event):
                self.world.newNode(mouseX, mouseY, *self.getNodeOptions())

        elif self.mode == 'constraint':
            if not self.selectedStartNode:
                self.selectedStartNode = self.findClosestNode(event)

                if self.selectedStartNode:
                    self.constraintPreviewLine = self.canvas.create_line(self.selectedStartNode.x, self.selectedStartNode.y,
                                                                         mouseX, mouseY, width=3, fill='#555', tags='preview')

            else:
                self.selectedEndNode = self.findClosestNode(event)

                if self.selectedEndNode:
                    # Don't allow creation of constraints with the same endpoints
                    overlapDetected = False
                    for constraint in self.world.getConstraints():
                        if (constraint.startPoint.x, constraint.startPoint.y) == (self.selectedStartNode.x, self.selectedStartNode.y) \
                                and (constraint.endPoint.x, constraint.endPoint.y) == (self.selectedEndNode.x, self.selectedEndNode.y):
                            overlapDetected = True

                    if not overlapDetected:
                        self.canvas.delete(self.constraintPreviewLine)
                        print(self.getConstraintOptions())
                        self.world.newConstraint(self.world.nodes.index(self.selectedStartNode), self.world.nodes.index(self.selectedEndNode), *self.getConstraintOptions())

                        self.selectedStartNode, self.selectedEndNode = None, None

        else:
            closestNode = self.findClosestNode(event)

            if closestNode:
                self.selectedNode = closestNode
                if closestNode.pinned: self.selectedNodeWasPinned = True
                self.selectedNode.pinned = True

            elif not self.playing:
                # The user is drawing a selection (not allowed when playing)
                self.selectedNodes = []
                self.selX1, self.selY1 = mouseX, mouseY

    def mouseMotion(self, event):
        # Draw constraint previews
        self.canvas.delete('preview')

        if self.selectedStartNode:
            self.constraintPreviewLine = self.canvas.create_line(self.selectedStartNode.x, self.selectedStartNode.y,
                                                                 event.x, event.y, width=3, fill='#555', tags='preview')
            # Send the constraint preview line to the back layer
            self.canvas.tag_lower(self.constraintPreviewLine)

    def mouseUp(self, event):
        if self.selectedNode:
            self.selectedNode.pinned = self.selectedNodeWasPinned
            self.selectedNode, self.selectedNodeWasPinned = None, False

        if self.selX1 and self.selY1:
            selectionBoundary = self.canvas.bbox(self.selectionBox or 0)
            self.canvas.delete(self.selectionBox or 0)
            self.selX1, self.selY1, self.selectionBox = None, None, None

            for node in self.world.getNodes():
                x, y = node.x, node.y

                if x > selectionBoundary[0] and x < selectionBoundary[2] \
                        and y > selectionBoundary[1] and y < selectionBoundary[3] \
                        and node not in self.selectedNodes:
                    self.selectedNodes.append(node) # type: ignore


if __name__ == '__main__':
    App()
