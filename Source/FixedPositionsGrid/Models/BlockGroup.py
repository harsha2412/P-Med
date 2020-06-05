
class BlockGroup:
    def __init__(self,id, polygon,point):
        self.id = id
        self.boundary  = polygon
        self.point = point
        self.pod = -1
        self.membership = -1
        self.demand = 0