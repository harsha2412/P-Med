from shapely.ops import cascaded_union
from matplotlib import pyplot as plt

class FixedPod:
    def __init__(self, id, point):
        self.id   = 'p'+str(id)
        self.coordinates = point
        self.bisectors = {} # stores m and c values for the current perpendicular corresponding to each POD
        self.myHomies = {} ## block Groups that have been assigned to me
        self.polygon = None
        self.plottableBoundary  = None
        self.balance = 0
        self.owner = -1


    def calculatePerpendicular(self, otherPod, w1, w2):
        sumWeight = w1 +w2
        #print('pods '+  str(self.id) + ", " + str(otherPod.id) )

        x = (w1*self.coordinates.x + w2*otherPod.coordinates.x)/(sumWeight)
        y= (w1 * self.coordinates.y + w2 * otherPod.coordinates.y) / (sumWeight)
        #print("Intersectionpoint point " + str(x) + ", " + str(y))
        self.bisectors[otherPod.id] = {}
        m = float(self.coordinates.x - otherPod.coordinates.x)/(otherPod.coordinates.y - self.coordinates.y)
        self.bisectors[otherPod.id]['m'] = m
        #print('m = '+ str(m))
        self.bisectors[otherPod.id]['c'] = y - m*x
        #print('c = ' + str(self.bisectors[otherPod.id]['c']))

    def storeSignsWithRespectToBisector(self, otherPod):
        val = self.coordinates.y - self.bisectors[otherPod.id]['m']*(self.coordinates.x) - self.bisectors[otherPod.id]['c']
        if val < 0:
            self.bisectors[otherPod.id]['sign'] = -1
        else:
            self.bisectors[otherPod.id]['sign'] = 1



    def getSignForThisPoinWithRespectToThisLine(self, point, line ):
        return point.y - line['m']*point.x - line['c']


    def createPolygon(self):
        #plt.figure()
        polygons = []
        count =1
        for b in self.myHomies:
            bg = self.myHomies.get(b)
            polygons.append(bg.boundary)
        self.plottableBoundary = gpd.GeoSeries(cascaded_union(polygons))
        self.polygon = cascaded_union(polygons)
        print("Pod ID "+  str(self.id) + str(len(self.myHomies) ))
       # print(self.polygon.exterior.coords[:])

        #self.plottableBoundary.plot(color = 'r')
       # plt.show()



    def printHomies(self):
        print("I am POd " + str(self.id) + "My Homies " )
        for b in self.myHomies:
            print(b)

        print("**************************************")