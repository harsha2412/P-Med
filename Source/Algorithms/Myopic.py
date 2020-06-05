import sys
import collections
import random
import math

from DAOs import SourceDAO
from DAOs import DestinationDAO
from Model import Source
from Model import Destination
import Utilities as util;
class Myopic:
    def __init__(self, k, distType):
        self.k = k
        self.currentSources = {}
        self.tempSources = {}
        self.destinations = {}
        self.sourceIdToDesinationIdMap = {}
        self.currentDestinationToSourceMapping = {}
        self.distanceMap = {}
        self.sourceDao = SourceDAO.SourceDAO(k, distType, 'Myopic')
        self.distType = distType
        self.destinationDao = DestinationDAO.DestinationDAO(distType)
        self.util = util.Utilities()


    def buildDistanceMap(self):
        print('Building distance map')
        for d1 in self.destinations:
            self.distanceMap[d1] = {}
            dest1 = self.destinations[d1]
            for d2 in self.destinations:
                dest2 = self.destinations[d2]
                distance = self.util.calculateDistanceBetweenDestinations(dest1, dest2)
                self.distanceMap[d1][d2] = distance
        print('done!!')
    def getAllDestinations(self):
        results = self.destinationDao.getAllSyntheticDestinations(self.distType)
        for row in results:
            newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
            self.destinations[newDestination.id] = newDestination
            newDestination.x = round(newDestination.x, 2)
            newDestination.y = round(newDestination.y, 2)
            #print('x = ' + str(newDestination.x)+ ', y = ' + str(newDestination.y))
        self.n = len(self.destinations)

    def pickMinSource(self,destination, sourceDict):
        min = sys.maxsize
        minSource = 1
        minsid = -1
        for source in sourceDict:
            sid = sourceDict[source].id
            #print("hererre "+ str(sid))
            s =sourceDict[source].destinationId
            if  round(self.distanceMap[s][destination]) < min:
                min = round(self.distanceMap[s][destination])
                minSource = s
                minsid = sid
        #print("closest source "+ str(minsid))
        sourceToUpdate =sourceDict.get(minsid)
        sourceDict.get(minsid).destinations.append(self.destinations.get(destination))
        return minSource


    def doCurrentAssignment(self, sourceDict):
        for s in sourceDict:
            sourceDict[s].destinations = []
        for d in self.destinations:
            self.currentDestinationToSourceMapping[d] = self.pickMinSource(d, sourceDict)


    def calculateCurrentCost(self):
        cost = 0.0
        for d in self.currentDestinationToSourceMapping:
            s = self.currentDestinationToSourceMapping[d]
            cost += self.distanceMap[s][d]*self.destinations.get(d).demand
        #print("Cost = " + str(cost) )
        return cost
    def checkCurrentSources(self, did):
        for s in self.currentSources:
            if self.currentSources.get(s).destinationId == did:
                return False
        return True
    def myopicAlgo(self):
        currentNumberOfSources = 1
        while currentNumberOfSources <= self.k:
            print("Adding source #"+ str(currentNumberOfSources))
            addingCost = sys.maxsize
            for did in self.destinations:
                dest = self.destinations.get(did)
                if self.checkCurrentSources(did): # destination not already a source
                    newSource = Source.Source(dest.x, dest.y, dest.id,currentNumberOfSources)
                    self.tempSources[currentNumberOfSources] = newSource
                    self.doCurrentAssignment(self.tempSources)
                    thisSourceCost = self.calculateCurrentCost()
                    if(addingCost > thisSourceCost):
                        #print("Candidate "+ str(did) + " cost = " + str(thisSourceCost))
                        addingCost = thisSourceCost
                        self.currentSources = dict(self.tempSources)

            currentNumberOfSources +=1
            self.tempSources = dict(self.currentSources)
        self.doCurrentAssignment(self.currentSources)
        print('Done with this shittt')
        return self.calculateCurrentCost()

    def getNewSource(self, source):
        xCoord = 0.0
        yCoord = 0.0
        size = len(source.destinations)
        xCoordw = 0.0
        yCoordw = 0.0
        demandSum = 0
        sizeForS = len(source.destinations)
        for ds in source.destinations:
            demandSum += ds.demand
        for dest in source.destinations:
            xCoord += dest.x
            yCoord += dest.y
            xCoordw += float(dest.demand) * dest.x
            yCoordw += float(dest.demand) * dest.y
        if (xCoord != 0.0 and sizeForS != 0):
            xCoordw = (xCoordw / demandSum)
            yCoordw = (yCoordw / demandSum)
        newMedian = self.findClosestDestination(xCoordw, yCoordw)
        if newMedian.id != source.destinationId:
            source = Source.Source(newMedian.x, newMedian.y, newMedian.id, source.id)
        return source


    def findClosestDestination(self, x, y):
        tempDestination = Destination.Destination(-1, x, y, 0)
        # print(" FInd closest for " + str(x) + ", " + str(y))
        minDistance = sys.maxsize
        closestDest = None
        for d in self.destinations:
            distance = self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), tempDestination)
            if minDistance > distance:
                # print("UPDATING MIN DISTANCE " + str(d))
                minDistance = distance
                closestDest = self.destinations.get(d)
        return closestDest

    def saveResultsToDatabase(self):
        print('do it ')
        self.sourceDao.createSourceTable(str(self.k) + '_myopic')
        self.sourceDao.populateSourceTable(self.currentSources,str(self.k) + '_myopic')
        self.sourceDao.createCatchmentAreas(self.currentSources,str(self.k) + '_myopic')

    def saveDestToSourceMapping(self):
        self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations)


    def calculateAverageDistanceCost(self):
        #currentKeys = [6,13,16,21,28, 32 ,36, 41, 51,63, 68 ,75,78,80,86,87, 93, 103,107,111, 117,122, 123,135,137,144,145,150,152,154,165,168  ] ## from sitation exchange
        currentKeys = [6,16,17,21, 33,36,39,46,51, 60, 67,78,85,93,100,103,108,111,118,122,123,125,137,142,145,150,152,155,159,162,169,171]
        currentKeys = [6, 16, 17, 21, 27, 28,  34, 46, 51, 57, 60,64,  67, 75, 80, 86, 93, 98, 108, 111, 118, 123, 140,  144, 145, 150, 152, 154, 159, 162, 165, 172] ## Lagrangioan
        #currentKeys = []
        i = 1
        self.currentSources = {}
        for k in currentKeys:
            dest = self.destinations.get(k)
            # self.tabooList[k] = dest
            source = Source.Source(dest.x, dest.y, dest.id, i)
            self.currentSources[i] = source
            i += 1
        self.doCurrentAssignment(self.currentSources)
        self.calculateCurrentCost()
        sourceAverage = 0
        demandSum = 0
        disAverage = 0
        weightedAverage = 0
        for d in self.destinations:
            dest = self.destinations.get(d)
            demandSum += dest.demand
        for d in self.destinations:
            dest = self.destinations.get(d)
            dest.weight = float(dest.demand) / demandSum
        ncheck = 0
        # print(len(self.currentSources))
        tdp = 0
        for s in self.currentSources:
            thisSource =0

            source = self.currentSources.get(s)
            print('\n*************\n source ' + str(source.destinationId))
            # print("Number of destinations for this source")
            # print(len(source.destinations))
            ncheck += len(source.destinations)
            for dest in source.destinations:
                source.totalDemand += dest.demand
                weightedAverage += (self.distanceMap[source.destinationId][dest.id]) * dest.weight
                disAverage += self.distanceMap[source.destinationId][dest.id]
            for dest in source.destinations:
                dp = round(self.distanceMap[source.destinationId][dest.id]) * dest.demand
                #print(str(dest.id) + ": dist --> " + str(round(self.distanceMap[source.destinationId][dest.id])) + "demamd "  + str(dest.demand) + " prod " + str(dp))
                tdp += dp

                thisSource += (round(self.distanceMap[source.destinationId][dest.id]) * dest.demand)
            print("Total demand for this source " + str(source.totalDemand))

            print("Cost for this source " + str(thisSource))
            thisSource = round(thisSource/source.totalDemand,2)
            print("Average for this source " + str(thisSource))
            sourceAverage += (thisSource*(source.totalDemand/demandSum))
        n = len(self.destinations)
        print("int cost " + str(tdp))

        #print("n = " + str(n))
        #print("ncheck = " + str(ncheck))
        print("*******\n\n")
        #print("Distance total " + str(disAverage / n))
        #print("Weighted Distance total " + str(weightedAverage / n))
        print("Source Weighted Distance total " + str(sourceAverage ))
        print("26 to 32 theirrs " + str(round(self.distanceMap[26][32])))
        print(str(self.destinations.get(26).x) + ", "+ str(self.destinations.get(26).y))
        print(str(self.destinations.get(42).x) + ", " + str(self.destinations.get(42).y))
        print("26 to 42 mine " + str(round(self.distanceMap[26][42])))
        print("26 to 43 mine " + str(round(self.distanceMap[26][43])))
        print("Gorttta  make sense")


        for d in self.currentDestinationToSourceMapping:
            print("Node " + str(self.destinations.get(d).id) + "(" + str(self.destinations.get(d).x) + ","+ str(self.destinations.get(d).y) + ")" + "--> "+ str(self.currentDestinationToSourceMapping[d]) + ", cost =" + str(round(self.distanceMap[d][self.currentDestinationToSourceMapping[d]]) *self.destinations.get(d).demand))
        #print(self.currentDestinationToSourceMapping)


