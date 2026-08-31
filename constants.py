#shared constants, grouped by where each one is actually used - so it's clear what touching a value will affect elsewhere:

# used everywhere: arena size and entity size
depth = 200  # size of play area, in world units
cube = 5     # size of the drone/interceptor, in world units

# main.py + interceptor.py
interception_radius = 100  # how close the drone must get to the launch site to trigger it

# main.py + rendering.py + interceptor.py
goal_radius = 20  # how close the drone must get to the goal to win

# main.py + rendering.py
ScreenW, ScreenH = 1200, 900

# drone.py + interceptor.py
drone_H_speed = 21  # horizontal cap
drone_V_speed = 10  # vertical cap
