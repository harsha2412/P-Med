from shapely.geometry import Point
from Model import  GridCell
import matplotlib.pyplot as plt
import random
class PMedianGrid:
    def __init__(self, size, population):
        self.population = population
        self.gridSize = size
        self.grid = {}

        self.gridDict = {}
        gid = 0
        for x in range(self.gridSize):
            if self.gridDict.get(x) is None:
                self.gridDict[x] = {}
            for y in range(self.gridSize):
                gc = GridCell.GridCell(gid, Point(x,y))
                self.grid[gid] = gc
                gid += 1
                self.gridDict[x][y] = gc
        #print("trying to plot")
        #self.plotGridPoint()
        #print("Done plotting")
        #exit(0)


    def distributePopulation(self):
        for i in range(self.population):
            cell = random.choice(self.grid)
            cell.pCount += 1


    def plotGridPoint(self):
        for p in self.grid:
            point = self.grid.get(p).point
            #print(str(point.x)+ ", " + str(point.y))
            plt.scatter(point.x, point.y, 7, 'b')
        plt.show()
