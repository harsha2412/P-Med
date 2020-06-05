import sys
import collections
import random

from DAOs import SourceDAO
from DAOs import DestinationDAO
from Model import Source
from Model import Destination
import Utilities as util;
class TeitzBart:
    def __init__(self, k, distType):
        self.k = k
        self.distType = distType
        self.maxIterations = 500
        self.iterations =0
        self.currentSources = {}
        self.newSources = {}
        self.minSources = {}
        self.destinations = {}
        self.sourceIdToDesinationIdMap = {}
        self.distanceMap = {}
        self.sourceDao = SourceDAO.SourceDAO(k, distType,  'TB')
        self.destinationDao = DestinationDAO.DestinationDAO(distType)
        self.util = util.Utilities()
        self.tabooList = {}
        #self.weightMap = {}
        self.currentDestinationToSourceMapping = {} # destination to source (id only)
        self.maxPopulation = 1
        self.current_r_value = 0.0

    def getAllDestinations(self):
        results = self.destinationDao.getAllSyntheticDestinations(self.distType)
        for row in results:
            newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
            self.destinations[newDestination.id] = newDestination
        self.n = len(self.destinations)

    def buildDistanceMap(self):
        for d1 in self.destinations:
            self.distanceMap[d1] = {}
            dest1 = self.destinations[d1]
            for d2 in self.destinations:
                dest2 = self.destinations[d2]
                distance = self.util.calculateDistanceBetweenDestinations(dest1, dest2)
                self.distanceMap[d1][d2] = distance

    def printCurrentSources(self):
        print("Printing current sources")
        for id in self.currentSources:
            source = self.currentSources[id]
            # print("Id = "+str(source.id))
            # print("X = "+str(source.x))
            # print("Y = "+str(source.y))
            print("Destination Id = " + str(source.destinationId))


    def printMinSources(self):
        print("Printing min sources")
        for id in self.minSources:
            source = self.minSources[id]
            # print("Id = "+str(source.id))
            # print("X = "+str(source.x))
            # print("Y = "+str(source.y))
            print("Destination Id = " + str(source.destinationId))
        #print("********************************")
        #print("Min Source Cost  " + self.)
    def calculateCurrentCost(self):
        cost = 0.0
        for d in self.currentDestinationToSourceMapping:
            s = self.currentDestinationToSourceMapping[d]
            cost += self.distanceMap[s][d]*self.destinations.get(d).demand
        #print("\n\nCost = "+ str(cost))
        return cost

    def pickMinSource(self, destination):
        min = sys.maxsize
        minSource = 1
        minsid = -1
        for source in self.currentSources:
            sid = self.currentSources[source].id
            # print("hererre "+ str(sid))
            s = self.currentSources[source].destinationId
            if self.distanceMap[s][destination] < min:
                min = self.distanceMap[s][destination]
                minSource = s
                minsid = sid
        # print("closest source "+ str(minsid))
        sourceToUpdate = self.currentSources.get(minsid)
        self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
        return minSource

    def doCurrentAssignment(self):
        for s in self.currentSources:
            self.currentSources.get(s).destinations = []
        for d in self.destinations:
            self.currentDestinationToSourceMapping[d] = self.pickMinSource(d)


    def tbStuff(self):
        print("")
        self.iterations = 0
        currentKeys = random.sample(list(self.destinations), self.k)
        i = 1
        self.currentSources = {}
        for k in currentKeys:
            dest = self.destinations.get(k)
            self.tabooList[k] = dest
            source = Source.Source(dest.x, dest.y, dest.id, i)
            i += 1
            self.currentSources[source.id] = source
        #print(" Initial Sources ")
        #self.printCurrentSources()
        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)


        self.doCurrentAssignment()
        self.current_r_value = self.calculateCurrentCost()
        terminationCondition = False
        iterations = 0
        self.iterations = 0
        while terminationCondition == False and iterations<self.maxIterations:
            #print("iteration " + str(iterations) )
            self.iterations +=1
            currentSourcesBackUp = dict(self.currentSources)
            v1_sources =  dict(self.currentSources)
            r_min_b = self.current_r_value
            bWinner = {}
            for comp in complementKeys:
                if self.tabooList.get(comp) is None:
                    dest_b = self.destinations.get(comp)
                    vertex_k = -1
                    delta_min = sys.maxsize
                    for vertex in v1_sources:


                        vj = v1_sources.get(vertex)
                        self.currentSources.update({vertex:Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment()
                        delta_bj = self.calculateCurrentCost() - self.current_r_value
                        self.currentSources =  dict(currentSourcesBackUp)
                        if delta_bj < 0 and delta_bj < delta_min:
                            delta_min = delta_bj
                            vertex_k = vertex
                    if vertex_k != -1:
                        toReplace = self.currentSources[vertex_k]
                        self.currentSources.update({vertex_k: Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment()
                        if self.calculateCurrentCost() < r_min_b:
                            r_min_b = self.calculateCurrentCost()
                            bWinner = dict(self.currentSources)
                        self.currentSources.update({vertex_k:toReplace})
                        self.doCurrentAssignment()

            if r_min_b < self.current_r_value:
                #print("r current defeated !!!")
                #print("r_current " + str(self.current_r_value)  +  " r_min_b " + str(r_min_b) )
                self.currentSources = dict(bWinner)
                self.current_r_value = r_min_b
                currentKeys = []
                for s in self.currentSources:
                    currentKeys.append(self.currentSources.get(s).destinationId)
                    self.tabooList.update({self.currentSources.get(s).destinationId:self.destinations.get(self.currentSources.get(s).destinationId)})
                complementKeys = []
                for d in self.destinations:
                    if d not in currentKeys:
                        complementKeys.append(d)

            else:
                self.doCurrentAssignment()
                terminationCondition = True
                print(" Ending Program==>  No improvement possible ")
            iterations += 1


    def tbStuffWithInitialSources(self, sourceDict):
        #currentKeys = random.sample(list(self.destinations), self.k)
        i = 1
        currentKeys = []

        self.currentSources = dict(sourceDict)
        for k in sourceDict:
            currentKeys.append(sourceDict.get(k).destinationId)

        #print(" Initial Sources ")
        #self.printCurrentSources()
        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)


        self.doCurrentAssignment()
        self.current_r_value = self.calculateCurrentCost()
        terminationCondition = False
        iterations = 0
        while terminationCondition == False and iterations<self.maxIterations:
            print("iteration " + str(iterations) )
            currentSourcesBackUp = dict(self.currentSources)
            v1_sources =  dict(self.currentSources)
            r_min_b = self.current_r_value
            bWinner = {}
            for comp in complementKeys:
                if self.tabooList.get(comp) is None:
                    dest_b = self.destinations.get(comp)
                    vertex_k = -1
                    delta_min = sys.maxsize
                    for vertex in v1_sources:
                        vj = v1_sources.get(vertex)
                        self.currentSources.update({vertex:Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment()
                        delta_bj = self.calculateCurrentCost() - self.current_r_value
                        self.currentSources =  dict(currentSourcesBackUp)
                        if delta_bj < 0 and delta_bj < delta_min:
                            delta_min = delta_bj
                            vertex_k = vertex
                    if vertex_k != -1:
                        toReplace = self.currentSources[vertex_k]
                        self.currentSources.update({vertex_k: Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment()
                        if self.calculateCurrentCost() < r_min_b:
                            r_min_b = self.calculateCurrentCost()
                            bWinner = dict(self.currentSources)
                        self.currentSources.update({vertex_k:toReplace})
                        self.doCurrentAssignment()

            if r_min_b < self.current_r_value:
                print("r current defeated !!!")
                print("r_current " + str(self.current_r_value)  +  " r_min_b " + str(r_min_b) )
                self.currentSources = dict(bWinner)
                self.current_r_value = r_min_b
                currentKeys = []
                for s in self.currentSources:
                    currentKeys.append(self.currentSources.get(s).destinationId)
                    self.tabooList.update({self.currentSources.get(s).destinationId:self.destinations.get(self.currentSources.get(s).destinationId)})
                complementKeys = []
                for d in self.destinations:
                    if d not in currentKeys:
                        complementKeys.append(d)
                iterations += 1
            else:
                self.doCurrentAssignment()
                terminationCondition = True
                print(" Ending Program==>  No improvement possible ")

    def completeTB(self):
        currentKeys = random.sample(list(self.destinations), self.k)
        i = 1
        self.currentSources = {}
        for k in currentKeys:
            dest = self.destinations.get(k)
            self.tabooList[k] = dest
            source = Source.Source(dest.x, dest.y, dest.id, i)
            i += 1
            self.currentSources[source.id] = source
        #print(" Initial Sources ")
        #self.printCurrentSources()
        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)


        self.doCurrentAssignment()
        self.current_r_value = self.calculateCurrentCost()
        terminationCondition = False
        iterations = 0
        while terminationCondition == False and iterations<self.maxIterations:
            print("iteration " + str(iterations) )
            currentSourcesBackUp = dict(self.currentSources)
            v1_sources =  dict(self.currentSources)
            r_min_b = self.current_r_value
            bWinner = {}
            for comp in complementKeys:
                if self.tabooList.get(comp) is None:
                    dest_b = self.destinations.get(comp)
                    vertex_k = -1
                    delta_min = sys.maxsize
                    for vertex in v1_sources:
                        vj = v1_sources.get(vertex)
                        self.currentSources.update({vertex:Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment()
                        delta_bj = self.calculateCurrentCost() - self.current_r_value
                        self.currentSources =  dict(currentSourcesBackUp)
                        if delta_bj < 0 and delta_bj < delta_min:
                            delta_min = delta_bj
                            vertex_k = vertex
                    if vertex_k != -1:
                        toReplace = self.currentSources[vertex_k]
                        self.currentSources.update({vertex_k: Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment()
                        if self.calculateCurrentCost() < r_min_b:
                            r_min_b = self.calculateCurrentCost()
                            bWinner = dict(self.currentSources)
                        self.currentSources.update({vertex_k:toReplace})
                        self.doCurrentAssignment()

            if r_min_b < self.current_r_value:
                print("r current defeated !!!")
                print("r_current " + str(self.current_r_value)  +  " r_min_b " + str(r_min_b) )
                self.currentSources = dict(bWinner)
                self.current_r_value = r_min_b
                currentKeys = []
                for s in self.currentSources:
                    currentKeys.append(self.currentSources.get(s).destinationId)
                    self.tabooList.update({self.currentSources.get(s).destinationId:self.destinations.get(self.currentSources.get(s).destinationId)})
                complementKeys = []
                for d in self.destinations:
                    if d not in currentKeys:
                        complementKeys.append(d)
                iterations += 1
            else:
                self.doCurrentAssignment()
                terminationCondition = True
                print(" Ending Program==>  No improvement possible ")




    def saveResultsToDatabase(self):
        self.sourceDao.createSourceTable()
        self.sourceDao.populateSourceTable(self.minSources)
        self.sourceDao.createCatchmentAreas(self.minSources)



    def saveDestToSourceMapping(self):
        self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations)

    def calculateAverageDistanceCost(self):
        currentKeys = [6,16,17,21, 27,28,35,46,57, 60, 64,67,75,80,86,93, 98,109,112,119,120,124,141,146,147,152,154,156,159,162,165,172]
        #currentKeys = [6,16,17,21, 33,36,39,46,51, 60, 67,78,85,93,100,103,108,111,118,122,123,125,137,142,145,150,152,155,159,162,169,171]
        i = 1
        self.currentSources = {}
        for k in currentKeys:
            dest = self.destinations.get(k)
            #self.tabooList[k] = dest
            source = Source.Source(dest.x, dest.y, dest.id, i)
            self.currentSources[i] = source
            i += 1
        self.doCurrentAssignment()
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
            dest.weight = float(dest.demand)/demandSum
        ncheck = 0
        #print(len(self.currentSources))

        for s in self.currentSources:
            source = self.currentSources.get(s)
            #print("Number of destinations for this source")
            #print(len(source.destinations))
            ncheck += len(source.destinations)
            for dest in source.destinations:
                source.totalDemand += dest.demand
                weightedAverage += (self.distanceMap[source.destinationId][dest.id])*dest.weight
                disAverage += self.distanceMap[source.destinationId][dest.id]
            for dest in source.destinations:
                sourceAverage += (self.distanceMap[source.destinationId][dest.id]*dest.demand)/source.totalDemand
        n = len(self.destinations)
        print("n = " + str(n))
        print("ncheck = " + str(ncheck))
        print("Distance total " + str(disAverage))
        print("Weighted Distance total " + str(weightedAverage))
        print("Source Weighted Distance total " + str(sourceAverage))
        print("*******\n\n")
        print("Distance total " + str(disAverage/n))
        print("Weighted Distance total " + str(weightedAverage/n))
        print("Source Weighted Distance total " + str(sourceAverage/self.k))