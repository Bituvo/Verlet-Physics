# Physics with Verlet Integration
This is a Python physics library to calculate verlet integration. It is easy and simple to use, and there are many options.

The rest of this documentation will assume that you have already imported the `verlet` library:
``` python
>>> import verlet
```

## Creating a World
Initialize a new world with `verlet.World`.

Parameters:
| Parameter | Type | Description |
| - | - | :- |
| `gravity` | `tuple` | A tuple containing the (horizontal, vertical) gravity, measured in units/second squared |
| `airFriction` | `float` | The air friction/drag coefficient, e.g. 0.99 for slight resistance
| `boundaryFunction` | `function` | A function that takes a `Node` object as input and modifies its position according to your boundaries |
| `timeStep` | `float` | The delta time of your simulation, e.g. 1 / FPS |

``` python
>>> def boundary(point):
...     x, y = node.x, node.y
...
...     if x < node.radius:
...         node.x = node.radius
...     if y < node.radius:
...         node.y = node.radius
...     if x > node.world.width - node.radius:
...         node.x = node.world.width - node.radius
...     if y > node.world.height - node.radius:
...         node.y = node.world.height - node.radius
...
>>> world = verlet.World((0, -32), 0.99, boundary, 1 / 60)
```

### World functions
### `world.newNode`

See ["Adding Things to Your World"](#adding-things-to-your-world)

### `world.newConstraint`

See ["Adding Things to Your World"](#adding-things-to-your-world)

### `world.countNodes -> int`

Returns how many nodes currently exist in the simulation
> **Warning**
> Do not use `len(world.nodes)`, as this list contains deleted nodes as well

### `world.countConstraints -> int`

Returns how many constraints currently exist in the simulation
> **Warning**
> Do not use `len(world.constraints)`, as this list contains deleted constraints as well

### `world.getNodeObject -> Union[None, Node]`

Returns the node object given its ID, allowing to manually change its properties

If the node was deleted, return None

Parameters:
| Parameter | Type | Description |
| - | - | :- |
| `ID` | `integer` | An ID returned by `world.newNode` |

### `world.getConstraintObject -> Union[None, Constraint]`

Returns the constraint object given its ID, allowing to manually change its properties

If the constraint was deleted, return None

Parameters:
| Parameter | Type | Description |
| - | - | :- |
| `ID` | `integer` | An ID returned by `world.newConstraint` |

### `world.getNodes -> tuple`

Returns all currently existing nodes in the simulation as objects
> **Warning**
> Do not use `world.nodes`, as this list contains deleted nodes as well

### `world.getConstraints -> tuple`

Returns all currently existing constraints in the simulation as objects
> **Warning**
> Do not use `world.constraints`, as this list contains deleted nodes as well

### `world.deleteNode`

Delete a node given its ID

This will also delete any attached constraints

Parameters:
| Parameter | Type | Description |
| - | - | :- |
| `ID` | `integer` | An ID returned by `world.newNode` |

### `world.deleteConstraint`

Delete a constraint given its ID

Parameters:
| Parameter | Type | Default | Description |
| - | - | - | :- |
| `ID` | `integer` | | An ID returned by `world.newNode` |
| `deleteConnectedNodes` | `boolean` | `False` | Whether or not to delete all nodes the constraint was a part of |

### `world.update`

Updates all nodes and constraints in the simulation

Parameters:
| Parameter | Type | Default | Description |
| - | - | - | :- |
| `updateRandomly` | `tuple` | (False, False) | Whether or not to randomly update the (nodes, constraints) |
| `constraintIterations` | `integer` | `1` | How many times to update the constraints, e.g. if you want them to be stiffer |

## Adding Things to Your World

You can add nodes and constraints to your simulation by using `world.newNode` and `world.newConstraint` respectively.

### `world.newNode -> int`

Creates a new node in the simulation, and returns its ID

Parameters:
| Parameter | Type | Default | Description |
| - | - | - | :- |
| `x` | `integer` or `float` | | The X position of the node |
| `y` | `integer` or `float` | | The Y position of the node |
| `xVel` | `integer` or `float` | `0` | The horizontal velocity of the node, measured in units/second |
| `yVel` | `integer` or `float` | `0` | The vertical velocity of the node, measured in units/second |
| `pinned` | `boolean` | `False` | Whether or not the node is restricted from moving |
| `radius` | `integer` or `float` | `5` | The radius of the node |

Example:

``` python
>>> node1 = world.newNode(100, 100, pinned=True)
>>> node2 = world.newNode(100, 200, yVel=10, radius=15)
```

### `world.newConstraint -> int`

Creates a new constraint in the simulation, and returns its ID

Parameters:
| Parameter | Type | Default | Description |
| - | - | - | :- |
| `startPoint` | `integer` | | A node ID returned by `world.newNode` |
| `endPoint` | `integer` | |  A node ID returned by `world.newNode` |
| `length` | `None` or `integer` or `float` | `None` | The target length of the constraint in units. If `None`, automatically calculate it |
| `stiffness` | `float` | `0.5` | The stiffness scalar of the constraint, higher = stiffer. Must be between 0 and 1

Example:

``` python
>>> constraint = world.newConstraint(node1, node2, stiffness=0.1) # Stretchy loose constraint
```

## More Information
### Nodes
 - Access the position of a node by using `node.x` and `node.y`
 - Get the velocity of a node by using `node.x - node.oldX` and `node.y - node.oldY`
 - Set a nodes radius with `node.radius = <number>`
 - Change if a node is pinned or not by using `node.pinned = <boolean>`
 
### Constraints
 - Change the length and stiffness of a constraint by using `constrant.length = <number>` and `constraint.stiffness = <scalar>`
 
## Obligatory Sandbox Screenshot
![image](https://user-images.githubusercontent.com/90872694/202856999-ee30fb41-cab8-4c7e-8cb4-8dc1348257bd.png)
