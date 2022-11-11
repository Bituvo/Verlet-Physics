from verlet import world, node, constraint
import tkinter as tk

def boundaryFunction(point):
    x, y = point.x, point.y

    if x < point.radius:
        point.x, point.oldX = [point.radius] * 2

    if x > point.world.width - point.radius:
        point.x, point.oldX = [point.world.width - point.radius] * 2

    if y < point.radius:
        point.y, point.oldY = [point.radius] * 2

    if y > point.world.height - point.radius:
        point.y, point.oldY = [point.world.height - point.radius] * 2

root = tk.Tk()
root.title('Verlet Square Demo')
root.resizable(0, 0)
root.wm_attributes('-fullscreen', True)

area = world.World(root.winfo_screenwidth(), root.winfo_screenheight(), (0, 0), 1, boundaryFunction)

points = [
    node.Node(area, 200, 200, velX=30),
    node.Node(area, 400, 200),
    node.Node(area, 400, 400),
    node.Node(area, 200, 400)
]

sticks = [
    constraint.Constraint(area, points[0], points[1]),
    constraint.Constraint(area, points[1], points[2]),
    constraint.Constraint(area, points[2], points[3]),
    constraint.Constraint(area, points[3], points[0]),
    constraint.Constraint(area, points[0], points[2]),
    constraint.Constraint(area, points[1], points[3])
]

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

    for point in points:
        velX = point.x + (point.x - point.oldX) * 3
        velY = point.y + (point.y - point.oldY) * 3

        canvas.create_line(point.x, point.y, velX, velY, width=2, fill='#f00')

    canvas.update()
    
    root.after(round(100 / 6), frame)

root.after(round(100 / 6), frame)
root.mainloop()
