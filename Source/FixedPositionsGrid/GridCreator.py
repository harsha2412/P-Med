from shapely.geometry import Point
import matplotlib.pyplot as plt
import random
class GridCreator:
    def __init__(self, size, nop):
        self.gridSize = size
        self.k = nop
        self.pods = []
        self.grid = []
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                self.grid.append(Point(x,y))
        self.getPodLocations()






    def plotGrid(self):
        fig = plt.figure()
        #ax = fig.add_subplot(111)
        #ax.add_collection(self.grid)
        x = [point.x for point in self.grid]
        y = [point.y for point in self.grid]
        px = [point.x for point in self.pods]
        py = [point.y for point in self.pods]
        plt.scatter(x,y,15, 'b')
        plt.scatter(px,py, 15, 'r', '*')
        plt.show()



    def getPodLocations(self):
        for i in range(self.k):
            x = random.random()*self.gridSize
            y = random.random()*self.gridSize
            self.pods.append(Point(x,y))
            print("Point cood" + str(x) + ', '+ str(y))

