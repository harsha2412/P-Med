class Destination:
    def __init__(self,id, x, y, demand):
        self.id = id
        self.x = x
        self.dx = -1 ## demand weighted centroid x
        self.dy = -1 ## demand weighted centroid x
        self.y = y
        self.demand = demand
        self.label = -1
        self.matrixIndex = -1

        self.weight = 1
        self.cells = []
