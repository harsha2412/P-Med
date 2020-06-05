import random, sys
from shapely.geometry import Point, Polygon, MultiPolygon, LinearRing, LineString
import numpy
from Utilities import Utilities
import matplotlib.pyplot as plt
from FixedPositionsGrid.Models import BlockGroup
from Cofig import  params
from Model import Destination
class MultiCenters:
    def __init__(self, pmGrid):
        self.pmgrid = pmGrid
        self.destinations = []
        self.region = {}
        self.util = Utilities()
        self.numberOfCenteres = params['MultiCenters']['number']


    def distributePopulation(self):
        # distribute 30% (inner) in 1/8*number th and 20(innerOuter) percent in the remaning 1/8*number at the centre, The rest 50 is randomly distribute in the outer area
        assignedPop = 0
        boundaries = {}
        print("Number of centers = "+ str(self.numberOfCenteres))
        for i in range(self.numberOfCenteres):
            center = random.choice(self.pmgrid.grid)
            innerStart = center.point.x - int (params['size']/(4*self.numberOfCenteres))
            innerEnd = center.point.x + int(params['size'] / (4 * self.numberOfCenteres))
            outerStart = center.point.x - int(params['size'] / (4 * self.numberOfCenteres))
            outerEnd = center.point.x + int(params['size'] / (4 * self.numberOfCenteres))

            innerStarty = center.point.y - int(params['size'] / (8 * self.numberOfCenteres))
            innerEndy = center.point.y + int(params['size'] / (8 * self.numberOfCenteres))
            outerStarty = center.point.y - int(params['size'] / (8 * self.numberOfCenteres))
            outerEndy = center.point.y + int(params['size'] / (8 * self.numberOfCenteres))

            while ( center.pCount>0 or outerStart <=0 or outerEnd >=params['size'] or outerStarty <=0 or outerEndy >=params['size']) :
                center = random.choice(self.pmgrid.grid)
                innerStart = center.point.x - int(params['size'] / (8 * self.numberOfCenteres))
                innerEnd = center.point.x + int(params['size'] / (8 * self.numberOfCenteres))
                outerStart = center.point.x - int(params['size'] / (4 * self.numberOfCenteres))
                outerEnd = center.point.x + int(params['size'] / (4 * self.numberOfCenteres))

                innerStarty = center.point.y - int(params['size'] / (8 * self.numberOfCenteres))
                innerEndy = center.point.y + int(params['size'] / (8 * self.numberOfCenteres))
                outerStarty = center.point.y - int(params['size'] / (4 * self.numberOfCenteres))
                outerEndy = center.point.y + int(params['size'] / (4 * self.numberOfCenteres))
                print("Trying &** CEnter " + str(center.point.x) + ", " + str(center.point.y))



            print("SUCEESS &** CEnter " + str(center.point.x)+", " + str(center.point.y) )
            #print("** outer start " + str(outerStart) +"innerStart " + str(innerStart))
            #print("** outer end " + str(outerEnd) + "innerEnd " + str(innerEnd))

            boundaries[i] = [outerStart, outerEnd]
            innerLength = int((params['totalPopulation']*params['inner'])/self.numberOfCenteres)
            for j in range(innerLength):
                randx = random.randint(innerStart, innerEnd)
                randy = random.randint(innerStarty, innerEndy)
                #print(str(randx) +", " + str(randy))
                self.pmgrid.gridDict[randx][randy].pCount += 1
            assignedPop += innerLength
            print("Assigned Pop " + str(assignedPop))
            innerOuterLength = int(params['totalPopulation'] * params['innerOuter']/self.numberOfCenteres)
            for j in range(innerOuterLength):
                randx = random.randint(outerStart, outerEnd)
                randy = random.randint(outerStarty, outerEndy)
                if randx <= innerEnd and randx >= innerStart and randy <= innerEndy and randy >= innerStarty:
                    p = random.random()
                    if p <= 0.5:
                        while (randx <= innerEnd and randx >= innerStart):
                            randx = random.randint(outerStart, outerEnd)
                    else:
                        while (randy <= innerEndy and randy >= innerStarty):
                            randy =  random.randint(outerStarty, outerEndy)
                self.pmgrid.gridDict[randx][randy].pCount += 1
            assignedPop += innerOuterLength
            print("Assigned Pop " + str(assignedPop))


        remainingPop = params['totalPopulation'] - assignedPop
        print("Remaning pop " + str(remainingPop))
        for i in range(remainingPop):
            randx = random.randint(0, params['size']-1)
            randy = random.randint(0, params['size']-1)
            unOccupied = False
            while (not unOccupied):
                unOccupied = True
                for b in boundaries:
                    xy = boundaries[b]
                    if randx <= xy[1] and randy >=xy[0]:
                        unOccupied = False
                        break
                randx = random.randint(0, params['size'] - 1)
                randy = random.randint(0, params['size'] - 1)
            self.pmgrid.gridDict[randx][randy].pCount += 1
        totPop = assignedPop+remainingPop
        print("Total POP" + str(totPop))

    def distributePopulationMoreClusters(self):
        # distribute 30% (inner) in 1/8*number th and 20(innerOuter) percent in the remaning 1/8*number at the centre, The rest 50 is randomly distribute in the outer area
        assignedPop = 0
        boundaries = {}
        print("Number of centers = "+ str(self.numberOfCenteres))
        populationAroundCenter = int((params['totalPopulation']*params['cluster'])/self.numberOfCenteres)
        for i in range(self.numberOfCenteres):
            center = random.choice(self.pmgrid.grid)
            rad = random.randint(3,9)
            startx = center.point.x - rad
            endx = center.point.x + rad
            starty = center.point.y - rad
            endy = center.point.y + rad
            print(rad)
            print(startx)
            print(starty)
            print(endx)
            print(endy)
            while (center.pCount > 0 or startx <= 0 or endx >= params['size'] or starty <= 0 or endy >= params['size']):
                center = random.choice(self.pmgrid.grid)
                startx = center.point.x - rad
                endx = center.point.x + rad
                starty = center.point.y - rad
                endy = center.point.y + rad
                print('pcount ' + str(center.pCount))
                print(startx)
                print(starty)
                print(endx)
                print(endy)
            print("SUCEESS &** CEnter " + str(center.point.x) + ", " + str(center.point.y))
            for j in range(populationAroundCenter):
                randx = random.randint(startx, endx)
                randy = random.randint(starty  ,endy)
                #print(str(randx) +", " + str(randy))
                self.pmgrid.gridDict[randx][randy].pCount += 1

            assignedPop += populationAroundCenter
            print("Assigned Pop " + str(assignedPop))
        remainingPop = params['totalPopulation'] - assignedPop
        print("Remaning pop " + str(remainingPop))
        for i in range(remainingPop):
            randx = random.randint(0, params['size'] - 1)
            randy = random.randint(0, params['size'] - 1)
            self.pmgrid.gridDict[randx][randy].pCount += 1
        totPop = assignedPop + remainingPop
        print("Total POP" + str(totPop))







    def getPopulationFromCellsInArray(self, array):
        count = 0
        for cellIndex in array:
            cell = self.pmgrid.grid.get(cellIndex)
            count += cell.pCount
        return count


    def createDestinations(self):
        mu = params['mean']
        std = params['std']
        assignedCells = []
        availableCells = []
        destination = Destination.Destination(1, -1,-1, 0 )
        demandToBeAssigned = int(numpy.random.normal(loc=mu, scale=std))
        assigned = 0
        print("grid size " +  str(len(self.pmgrid.grid)))
        assignedCellIndex = 0
        i = self.pmgrid.grid[0]
        totalPop = 0
        for cellIndex in self.pmgrid.grid:
            cell = self.pmgrid.grid.get(cellIndex)
            availableCells.append(cell.id)
            totalPop+= cell.pCount
        print("sum of cellss = " + str(totalPop))
        pop = 0
        did = 1
        minCell = None
        while assigned < len(self.pmgrid.grid) and len(availableCells) > 0 :
            if len( destination.cells) ==0 or destination.demand > demandToBeAssigned:
                #print("Assigned = " + str(assigned))
                print("Population till now= " + str(pop))
                assigendPop = self.getPopulationFromCellsInArray(assignedCells)
                remainingPop = self.getPopulationFromCellsInArray(availableCells)
                print("assigned POP " + str(assigendPop) + ", available pop " + str(remainingPop))
                t = assigendPop + remainingPop
                print("total - " + str(t))
                print("\n\n OO Lala New Destination")
                if destination.demand >= demandToBeAssigned:
                    self.destinations.append(destination)


                print("assignment status for" + str(i.id) + " is "+ str(i.assigned))

                if i.id in availableCells:
                    i.assigned = True
                    destination = Destination.Destination(did, -1, -1, 0)
                    did += 1
                    destination.cells.append(i)
                    availableCells.remove(i.id)
                    assignedCells.append(i.id)
                    destination.x = i.point.x
                    destination.y = i.point.y
                    destination.demand += i.pCount
                    assigned = len(assignedCells)
                    pop+=i.pCount


                demandToBeAssigned = int(numpy.random.normal(loc=mu, scale=std))
                print("Demand to be assigned " + str(demandToBeAssigned) )
            while(destination.demand <= demandToBeAssigned ):
                #print("current demand = " + str(destination.demand))
                #print("Total POP assigned " + str(pop) )
                if (assigned < len(self.pmgrid.grid) and pop <=totalPop ):
                    if (len(availableCells) >0 ):
                        #print("Available Cells " + str(len(availableCells)))
                        #print("Assigned gc = " + str(assigned))
                        median= self.getCurrentMedian(destination)
                        minCell = self.getClosestCell(median, availableCells)
                    #print("assignment status for " + str(minCell) + str(minCell.assigned))
                        if minCell.id in availableCells:
                            assignedCells.append(minCell.id)
                            availableCells.remove(minCell.id)
                            destination.cells.append(minCell)
                            minCell.assigned = True
                            destination.demand += minCell.pCount
                            pop += minCell.pCount
                            assigned = len(assignedCells)
                        else:
                            print("Blasphemy")
                            print(availableCells)
                            print("Min cell id" +str(minCell.id))
                    else:
                        break
                else:
                    break

            if minCell is not None  :
                if len(availableCells) > 0:
                    i = self.getClosestCell(minCell.point, availableCells)
                else:
                    break



            print("Available Cells " + str(len(availableCells)))
            print("assigned Cells " + str(len(assignedCells)))
            if pop > totalPop:
                break


            print("DID: " + str(did))
        print("Len of assigned cells = " +str(len(assignedCells)))
        print("Len of available cells = " + str(len(availableCells)))

    def createRegion(self):
        bgCount = 1
        for dest in self.destinations:
            boundary = dest.cells[0].polygon
            for cell in dest.cells:
                boundary = boundary.union(cell.polygon)
            Bg= BlockGroup.BlockGroup(bgCount, boundary, self.getCurrentMedian(dest))
            Bg.demand = dest.demand
            self.region[bgCount] = Bg
            bgCount += 1



    def plotRegion(self):
        fig, axs = plt.subplots()
        for bid in self.region:
            b = self.region.get(bid)
            xs,ys = b.boundary.exterior.xy
            plt.plot(xs,ys, c='b')
            plt.scatter(b.point.x, b.point.y, 15, 'g')
        plt.show()







    def getCurrentMedian(self, destination):
        xSum = 0
        ySum = 0
        for cell in destination.cells:
            xSum += cell.point.x
            ySum += cell.point.y
        pt = Point(xSum/(len(destination.cells)), ySum/(len(destination.cells)))
        return pt

    def getClosestCell(self,currentCenter, availableCells ):
        minCell  = self.pmgrid.grid.get(availableCells[0])
        minDistance = sys.maxsize
        for cellIndex in availableCells:
            cell = self.pmgrid.grid.get(cellIndex)
            if cell.assigned:
                print("HOW?? Blasphemyyyy\n\n")
            if self.util.calculateDistanceBetweenPoints(currentCenter, cell.point) < minDistance:
                minCell = cell
                minDistance = self.util.calculateDistanceBetweenPoints(currentCenter, cell.point)
        if minCell.id in availableCells:
            return minCell





