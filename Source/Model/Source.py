import sys
class Source:
    def __init__(self, x, y, destinationId, id):
        self.x = x
        self.y = y
        self.destinationId = destinationId
        self.capacity = sys.maxsize
        self.destinations = []
        self.id = id
        self.cost = 0.0
        self.weightedx = 0
        self.weightedy = 0
        self.ax = 0.0
        self.ay = 0.0
        self.totalDemand= 0
        self.label = -1


