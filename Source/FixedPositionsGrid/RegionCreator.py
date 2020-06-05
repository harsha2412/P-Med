from shapely.geometry import Point, Polygon, MultiPolygon, LinearRing, LineString
import random
import matplotlib
from shapely.ops import cascaded_union
from FixedPositionsGrid.Models import BlockGroup
from FixedPositionsGrid.Models import FixedPod
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

class RegionCreator:
    def __init__(self, size, nop):
        self.region = {}
        self.regionShape = None
        self.k = nop
        self.pods = {}
        self.size = size
        origin = Point(0,0)
        offset = 1
        count = 1
        self.colorMap = {}
        colors = cm.Dark2(np.linspace(0, 1, self.k)) # inferno rainbow ,agma Set1 # https://matplotlib.org/examples/color/colormaps_reference.html
        for i in range(self.k):
            self.colorMap['p'+str(i+1)] = colors[i]
        self.regionShape =  Polygon([(origin.x, origin.y), (origin.x, origin.y + offset), (origin.x+offset, origin.y + offset), (origin.x+offset, origin.y),  ])
        for x in range(self.size):
            rowOrigin = origin
            for y in range(self.size):
                p = Polygon([(origin.x, origin.y), (origin.x, origin.y + offset), (origin.x+offset, origin.y + offset), (origin.x+offset, origin.y)  ])
                centroid = p.centroid
                bg = BlockGroup.BlockGroup(count, p, centroid )
                self.region[count] = bg
                count +=1
                origin = Point(origin.x+offset, origin.y)
                if y == self.size -1:
                    origin = Point(rowOrigin.x, rowOrigin.y +offset)
        self.getPodLocations()
        origin = Point(0, 0)
        self.regionShape = Polygon([(origin.x, origin.y), (origin.x, origin.y + size), (origin.x+size, origin.y + size), (origin.x+size, origin.y) ])
        print(self.regionShape.exterior.coords[:])
        #self.plotRegionSeparately()
        #self.getEntireRegionPolygon()

    def getPodLocations(self):
        nob = len(self.region)
        tabooList = []

        for i in range(self.k):
            podl = random.randint(1, nob )
            while podl in tabooList:
                podl =  random.randint(1, nob )
            tabooList.append(podl)
            min_x, min_y, max_x, max_y = self.region[podl].boundary.bounds
            randomPoint = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
            #x = self.region[podl].point.x
            #y = self.region[podl].point.y
            #x = random.random() * self.size
            #y = random.random() * self.size
            newPod = FixedPod.FixedPod(i+1, randomPoint)
            newPod.owner = podl
            self.pods[newPod.id] = newPod
            print( 'Point(['+ str(randomPoint.x) + ', ' + str(randomPoint.y) + '])')


        self.pods['p1'].coordinates = Point([14.830850276266986, 27.88208576682921])
        self.pods['p2'].coordinates = Point([26.338930193505522, 4.251064898784021])
        self.pods['p4'].coordinates = Point([3.79294539296631, 1.08799978252132878])
        self.pods['p5'].coordinates = Point([0.08745314851043307, 14.60847846574841])
        self.pods['p6'].coordinates = Point([25.501315785110407, 28.9869275922433])
        self.pods['p7'].coordinates = Point([15.351017277251263, 5.705713934941022])
        self.pods['p8'].coordinates = Point([20.242033879857702, 7.9905919526155023])
        self.pods['p9'].coordinates = Point([1.3070667846657935, 27.258253310591776])
        self.pods['p3'].coordinates = Point([13.763482863984963, 17.38927238731466])
        self.pods['p10'].coordinates = Point([28.338930193505522, 15.251064898784021])

        self.findPodsOwner()
        '''
             self.pods['p1'].coordinates = Point([1.9, 2.5])
        self.pods['p2'].coordinates = Point([2.9,0.1])
        self.pods['p3'].coordinates = Point([3.75, 2.75])
        self.pods['p4'].coordinates = Point([2.8, 2.4])
        self.pods['p5'].coordinates = Point([0.4, 1.1])
        self.findPodsOwner()
            Point cood7.064681762868536, 0.36655967396749156
    Point cood7.59293991145275, 4.469328752565419
    Point cood0.3257717091317983, 3.4571437613515967
    Point cood0.6068872447611557, 7.773408957410974
    Point cood1.1136848900715248, 4.279589915652524
            '''

    def plotRegion(self):
        fig, axs = plt.subplots()
        for bid in self.region:
            b = self.region.get(bid)
            xs,ys = b.boundary.exterior.xy
            plt.plot(xs,ys, c='b')
            plt.scatter(b.point.x, b.point.y, 15, 'g')
        for pid in self.pods:
            p = self.pods.get(pid)
            plt.scatter(p.coordinates.x, p.coordinates.y, 60, 'r', 'o')
            #x.append(xs)
            #y.append(ys)

        #axs.fill(xs, ys, alpha=0.5, fc='r', ec='none')
        #axs.fill(xs1, ys1, alpha=0.5, fc='r', ec='none')
        #plt.plot(xs,ys)
        #plt.plot(self.regionShape.exterior.xy, c='m')
        #plt.show()

    def getEntireRegionPolygon(self):
        polygons = []
        for bid in self.region:
            b =self.region.get(bid)
            polygons.append(b.boundary)
        m = MultiPolygon(polygons)
        self.regionShape = cascaded_union(m)



    def plotPartitions(self):
        fig, axs = plt.subplots()
        for bid in self.region:
            b = self.region.get(bid)
            xs, ys = b.boundary.exterior.xy
            plt.plot(xs, ys, c='k')
            axs.fill(xs, ys, alpha=0.3, fc=self.colorMap[b.membership], ec='none')
            plt.scatter(b.point.x, b.point.y, 15, color = self.colorMap[b.membership])
        x = []
        y = []
        n = []
        for pid in self.pods:
            p = self.pods.get(pid)
            n.append(pid)
            x.append(p.coordinates.x)
            y.append(p.coordinates.y)

        axs.scatter(x, y ,60, color='r', marker='o' )
        i = 0
        #for i,text in enumerate(n):
         #   axs.annotate(text, (x[i], y[i]))

            #plt.scatter(p.coordinates.x, p.coordinates.y, 34, color=self.colorMap[p.id], marker='X')
        plt.show()


    def plotInitialPartitions(self):
        fig, axs = plt.subplots()
        for bid in self.region:
            b = self.region.get(bid)
            xs, ys = b.boundary.exterior.xy
            plt.plot(xs, ys, c='k')
            axs.fill(xs, ys, alpha=0.3, fc=self.colorMap[b.membership], ec='none')
            plt.scatter(b.point.x, b.point.y, 15, color = self.colorMap[b.membership])
        x = []
        y = []
        n = []
        for pid in self.pods:
            p = self.pods.get(pid)
            n.append(pid)
            x.append(p.coordinates.x)
            y.append(p.coordinates.y)

        axs.scatter(x, y ,60, color='r', marker='o' )
        i = 0
        #for i,text in enumerate(n):
            #axs.annotate(text, (x[i], y[i]))

            #plt.scatter(p.coordinates.x, p.coordinates.y, 34, color=self.colorMap[p.id], marker='X')
        plt.draw()


    def plotPartition3ForTesting(self):
        #fig, axs = plt.subplots()
        #xs, ys = self.pods['p3'].polygon.boundary.exterior.xy
        #plt.plot(xs, ys, c='k')
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        self.pods['p3'].plottableBoundary.plot(ax=ax,color='r', alpha = 0.5)
        self.pods['p5'].plottableBoundary.plot(ax=ax,color='b', alpha =0.5)
        self.pods['p1'].plottableBoundary.plot(ax=ax,color='m', alpha=0.5)
        self.pods['p4'].plottableBoundary.plot(ax=ax,color='k', alpha=0.5)
        self.pods['p2'].plottableBoundary.plot(ax=ax, color='g', alpha=0.5)
        plt.draw()



    def findPodsOwner(self):
        for p, pod in self.pods.items():
            for b, bg in self.region.items():
                if pod.coordinates.within(bg.boundary):
                    pod.owner = b
                    break

    def plotPartition3ForTesting(self):
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        for p  in self.pods:
            self.pods[p].plottableBoundary.plot(ax=ax, color=self.colorMap[p], alpha=0.5)
        plt.draw()


    # def plotRegionSeparately(self):
    #     fig, axs = plt.subplots()
    #     self.regionShape = Polygon([(0,0),(0,5), (5,5), (5,0)])
    #     plt.plot(self.regionShape.exterior.xy, c='m')
    #     plt.show()



















# #constructing the first rect as a polygon
# r1 = sg.Polygon([(0,0),(0,1),(1,1),(1,0),(0,0)])
#
# #a shortcut for constructing a rectangular polygon
# r2 = sg.box(0.5,0.5,1.5,1.5)
#
# #cascaded union can work on a list of shapes
# new_shape = so.cascaded_union([r1,r2])
#
# #exterior coordinates split into two arrays, xs and ys
# # which is how matplotlib will need for plotting
# xs, ys = new_shape.exterior.xy
#
# #plot it
# fig, axs = plt.subplots()
# axs.fill(xs, ys, alpha=0.5, fc='r', ec='none')
# plt.show() #if no