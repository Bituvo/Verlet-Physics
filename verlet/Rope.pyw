from verlet import world, node, constraint
from time import sleep, process_time
import tkinter as tk

JOINTS = 30
DISTANCE = 20

def boundaryFunction(node):
    x, y = node.x, node.y

    if x < node.radius:
        node.x = node.radius
    if y < node.radius:
        node.y = node.radius
    if x > node.world.width - node.radius:
        node.x = node.world.width - node.radius
    if y > node.world.height - node.radius:
        node.y = node.world.height - node.radius
        # Apply ground friction
        velX = (node.x - node.oldX) * 0.8
        node.oldX = node.x - velX

root = tk.Tk()
root.title('Verlet Square Demo')
root.resizable(False, False)
root.wm_attributes('-fullscreen', True)

area = world.World(root.winfo_screenwidth(), root.winfo_screenheight(), (0, -98), 0.99, boundaryFunction, 1 / 60)

points = []
sticks = []

x = area.width / 2
y = area.height / 2 - (JOINTS * DISTANCE / 2) - DISTANCE
for i in range(JOINTS):
    points.append(node.Node(area, x, y, radius=5))
    y += DISTANCE

for i in range(JOINTS - 1):
    sticks.append(constraint.Constraint(area, points[i], points[i + 1], stiffness=1))

canvas = tk.Canvas(root, width=area.width, height=area.height, bg='#fff', highlightthickness=0)
canvas.pack()

mouseX, mouseY = None, None

def mouseDown(event):
    global mouseX, mouseY
    mouseX, mouseY = event.x, event.y
    
def dragPoint(event):
    global mouseX, mouseY
    mouseX, mouseY = event.x, event.y
    
def mouseUp(event):
    global mouseX, mouseY
    mouseX, mouseY = None, None

canvas.bind('<Button-1>', mouseDown)
canvas.bind('<B1-Motion>', dragPoint)
canvas.bind('<ButtonRelease-1>', mouseUp)

def frame():
    canvas.delete('all')

    for point in points: point.update()
    for i in range(50):
        for stick in sticks: stick.update()

    for i, point in enumerate(points):
        if i == 0 and mouseX and mouseY:
            point.pinned = True
            point.x += (mouseX - point.x) / 5
            point.y += (mouseY - point.y) / 5

            point.oldX, point.oldY = point.x, point.y
            
        elif i == 0 and not mouseX and not mouseY:
            point.pinned = False
            
        x1, y1 = point.x - point.radius, point.y - point.radius
        x2, y2 = point.x + point.radius, point.y + point.radius

        canvas.create_oval(x1, y1, x2, y2, outline='', fill='#000')

    for stick in sticks:
        x1, y1 = stick.startPoint.x, stick.startPoint.y
        x2, y2 = stick.endPoint.x, stick.endPoint.y

        canvas.create_line(x1, y1, x2, y2, width=3)

    canvas.update()

while True:
    t1 = process_time()
    frame()
    t2 = process_time()

    if t2 - t1 > 1 / 60:
        continue
    else:
        sleep(1 / 60 - (t2 - t1))
