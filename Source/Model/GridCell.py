from shapely.geometry import Point, Polygon
class GridCell:
    def __init__(self,id, point):
        self.point = point
        self.id = id
        self.pCount = 0
        offset = 1
        self.polygon = Polygon([(point.x, point.y), (point.x, point.y + offset), (point.x+offset, point.y + offset), (point.x+offset, point.y),  ])
        self.assigned = False