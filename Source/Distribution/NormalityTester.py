import math
from shapely.geometry import Point, Polygon, MultiPolygon
from Cofig import params
from decimal import  Decimal
from DAOs import  DestinationDAO
from scipy.stats import chisquare
class NormalityTester:
    def __init__(self, points, util, boundingBox, region):
        self.points = points
        self.binSize  = math.ceil(len(points) ** (1. / 3))
        self.numberOfBins = int(len(points)/self.binSize)
        self.actualBinSize = len(points)/self.numberOfBins
        self.distanceMap = {}
        self.util = util
        self.bins = {}
        self.expectedBinFrequency = {}
        self.observedBinFrequency = {}
        self.unitCellSize = params['unitCell']
        self.boundingBox = boundingBox
        self.grid = {}
        self.region = region
        self.createGridCellsOverBoundingBox()



    def buildDistanceMap(self):
        for p in self.points:
            self.distanceMap[p.id] = {}
            for p1 in self.points:
                if p.id != p1.id:
                    self.distanceMap[p.id][p1.id] = self.util.calculateDistanceBetweenDestinations(p,p1)

    def createGridCellsOverBoundingBox(self):
        x = self.boundingBox['xmin']
        y = self.boundingBox['ymin']
        i = 1
        offset = self.unitCellSize
        origin = Point(x,y)
        count = 1
        gridMultiList = []
        while x<=self.boundingBox['xmax']:
            y = self.boundingBox['ymin']
            while y<=self.boundingBox['ymax']:
                p = Polygon([(x, y), (x, y + offset), (x + offset, y + offset), (x + offset, y)])
                if p.intersects(self.region):
                    gridMultiList.append(p)
                    cell = GridCell(count, Point(x, y), Point(x + offset, y + offset), p)
                    self.grid[count] = cell
                    count += 1
                y+= offset
            x+=offset
        self.numberOfBins = len(self.grid)
        #print("i = " + str(i))
        #print("Number of bins  =  "+ str(self.numberOfBins))
        #destDao = DestinationDAO.DestinationDAO("Random")
        #destDao.saveGridOverPart(gridMultiList, self.region)



    def populateObservedBins(self):
        for pt in self.points:
            for cellId in self.grid:
                cell =self.grid.get(cellId)
                if cell.checkIfPointWithinCell(Point(pt.x, pt.y)):
                    cell.points.append(pt.id)
                    break
        for cellId in self.grid:
            cell =self.grid.get(cellId)
            nPts = len(cell.points)
            if self.observedBinFrequency.get(nPts) is None:
                self.observedBinFrequency[nPts] = 1
            else:
                self.observedBinFrequency[nPts] += 1

        i = 0
        while i <= len(self.points):
            if self.observedBinFrequency.get(i) is None:
                self.observedBinFrequency[i] = 0
            i+=1


    def chiSquaredTest(self):
        self.populateObservedBins()
        self.getExpectedCount()
        f_obs = []
        f_exp = []
        i = 0
        #print("Number of points " + str(len(self.points)))
        while i <= len(self.points):
            if self.expectedBinFrequency.get(i)==0:
                self.expectedBinFrequency[i] = 0.0000000000000000001
            f_obs.append(self.observedBinFrequency.get(i))
            f_exp.append(self.expectedBinFrequency.get(i))
            i+=1
        chiPython = chisquare(f_obs, f_exp)
        #print('Python Chi Value ' + str(chiPython))
        if chiPython.pvalue < params['statsAlpha']:
            return False
        else:
            return True










    def getExpectedCount(self):
        i = 0
        while i <=len(self.points):
            probBinSelection = 1.0/self.numberOfBins
            self.expectedBinFrequency[i] = float(Decimal(self.numberOfBins)*(self.nChooseR(len(self.points), i))*Decimal(probBinSelection**i*(1-probBinSelection)**(len(self.points)-i)))
            i+=1


    def nChooseR(self, n, r):
        #print('n' + str(n))
        #print('r ' + str(r))
        res =  Decimal(math.factorial(n)//(math.factorial(r)* math.factorial(n-r)))
        #print(res)
        return  res

    def checkForNormality(self):
        return self.chiSquaredTest()

class GridCell:
    def __init__(self, id, point1, point2, polygon):
        self.id = id
        self.bottomLeftCorner =point1
        self.topRightCorner = point2
        self.points= []
        self.polygon = polygon

    def checkIfPointWithinCell(self, point):
        if point.x <= self.topRightCorner.x and point.x >= self.bottomLeftCorner.x and point.y <= self.topRightCorner.y and point.y >= self.bottomLeftCorner.y:
            return True
        else:
            return False




