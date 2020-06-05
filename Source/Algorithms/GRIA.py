import sys
import collections
import random
from Cofig import  params
from DAOs import SourceDAO
from DAOs import DestinationDAO
from Model import Source
from Model import Destination
import Utilities as util
import multiprocessing
import csv

class GRIA:
    def __init__(self, k, distType):
        self.k = k
        self.maxIterations = 500
        self.distType = distType
        self.currentSources = {}
        self.newSources = {}
        self.minSources = {}
        self.destinations = {}
        self.iterations = 0
        self.sourceIdToDesinationIdMap = {}
        self.distanceMap = {}
        self.sourceDao = SourceDAO.SourceDAO(k, distType, 'GRIA')
        self.destinationDao = DestinationDAO.DestinationDAO(distType)
        self.util = util.Utilities()
        self.tabooList = {}
        #self.weightMap = {}
        self.currentDestinationToSourceMapping = {} # destination to source (id only)
        self.maxPopulation = 1
        self.current_r_value = 0.0
        self.globalSwap = True
        self.bothSwap = True
        self.localSwap = False
        self.localSwapCount = 0
        self.globalSwapCount= 0
        self.destIdToSourceId = {}


    def getAllDestinations(self):
        results = self.destinationDao.getAllSyntheticDestinations(self.distType)
        for row in results:
            newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
            newDestination.x = round(newDestination.x, 4)
            newDestination.y = round(newDestination.y, 4)
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

    def pickMinSource(self,destination, sourceDict):
        min = sys.maxsize
        minSource = 1
        minsid = -1
        for source in sourceDict:
            sid = sourceDict[source].id
            #print("hererre "+ str(sid))
            s =sourceDict[source].destinationId
            if destination == s:
                minSource = s
                minsid = sid
                break
            else:
                if  self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(destination)) < min:
                    min = self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(destination))
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
        self.destIdToSourceId = {}
        for s in sourceDict:
            source = sourceDict.get(s)
            self.destIdToSourceId[source.destinationId] = s

    def calculateCurrentCost(self):
        cost = 0.0
        for d in self.currentDestinationToSourceMapping:
            s = self.currentDestinationToSourceMapping[d]
            cost += self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(d))*self.destinations.get(d).demand
        return cost

    def checkCurrentSources(self, did, sourceDict):
        for s in sourceDict:
            if sourceDict.get(s).destinationId == did:
                return False
        return True

    def singleGlobalStep(self):
        currentCost = self.calculateCurrentCost()
        tempDict = dict(self.currentSources)
        dropOptima = {}
        idToUpdate = -1
        dropCost = sys.maxsize
        ## DROP PART
        backUpMapping = {}
        for d in self.destinations:
            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
        for s in self.currentSources:
            removedSource = self.currentSources[s]
            del tempDict[s]
            for d in removedSource.destinations:
                self.currentDestinationToSourceMapping[d.id] = self.pickMinSource(d.id, tempDict)
                # self.doCurrentAssignment(tempDict)
                # self.doCurrentAssignment(tempDict)
            tempCost = self.calculateCurrentCost()
            if dropCost > tempCost:
                dropCost = tempCost
                idToUpdate = s
                dropOptima = dict(tempDict)
            tempDict[s] = removedSource
            self.currentDestinationToSourceMapping = {}
            for d in backUpMapping:
                self.currentDestinationToSourceMapping[d] = backUpMapping[d]

        ## ADD PART
        addOptima = {}
        tempDict = dict(dropOptima)
        addCost = sys.maxsize
        backUpMapping = {}
        self.doCurrentAssignment(dropOptima)
        for d in self.destinations:
            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
        backUpInverseMapping = {}
        for d in self.destIdToSourceId:
            backUpInverseMapping[d] = self.destIdToSourceId[d]
        for d in self.destinations:
            if self.checkCurrentSources(d, dropOptima):
                dest = self.destinations[d]
                newSource = Source.Source(dest.x, dest.y, dest.id, idToUpdate)
                tempDict[idToUpdate] = newSource
                for d in self.destinations:
                    dest = self.destinations.get(d)
                    currentSourceDid = self.currentDestinationToSourceMapping[d]
                    sourceId = self.destIdToSourceId[currentSourceDid]
                    source = self.currentSources.get(sourceId)
                    currentDistance = self.util.calculateDistanceBetweenDestinations(dest, source)
                    newDistance = self.util.calculateDistanceBetweenDestinations(dest, newSource)
                    if newDistance < currentDistance:
                        self.currentDestinationToSourceMapping[d] = newSource.destinationId
        
                # self.doCurrentAssignment(tempDict)
                tempCost = self.calculateCurrentCost()
                if addCost > tempCost:
                    addCost = tempCost
                    addOptima = dict(tempDict)
                del tempDict[idToUpdate]
                self.currentDestinationToSourceMapping = {}
                for d in self.destinations:
                    self.currentDestinationToSourceMapping[d] = backUpMapping[d]
        if addCost - currentCost < 0 :
            self.currentSources = dict(addOptima)
            self.doCurrentAssignment(self.currentSources)
            return True
        else:
            self.doCurrentAssignment(self.currentSources)
            return False

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

    def getNewSource(self, source):
        xCoord = 0.0
        yCoord = 0.0
        size = len(source.destinations)
        xCoordw = 0.0
        yCoordw = 0.0
        demandSum = 0
        sizeForS  = len(source.destinations)
        for ds in source.destinations:
            demandSum += ds.demand
        for dest in source.destinations:
            xCoord+= dest.x
            yCoord+= dest.y
            xCoordw += float(dest.demand) * dest.x
            yCoordw += float(dest.demand) * dest.y
        if (xCoord != 0.0 and sizeForS != 0):
            xCoordw = (xCoordw / demandSum)
            yCoordw = (yCoordw / demandSum)
            xCoord = xCoord/sizeForS
            yCoord = yCoord/sizeForS
        newMedian = self.findClosestDestination(xCoordw, yCoordw)
        if newMedian.id != source.destinationId:
            source = Source.Source(newMedian.x, newMedian.y, newMedian.id, source.id)
        return source


    def solveOneMedianProblem(self):
        print(" This part needs only a single facility")
        self.currentSources = {}
        minCost = sys.maxsize
        for d in self.destinations:
            dest = self.destinations[d]
            self.currentSources[1] = Source.Source(dest.x, dest.y, dest.id, 1)
            self.doCurrentAssignment(self.currentSources)
            cost  = self.calculateCurrentCost()
            if minCost > cost:
                minCost = cost
                self.minSources = dict(self.currentSources)

        self.currentSources = dict(self.minSources)





    def griaStuff(self):
        self.localSwapCount = 0
        self.globalSwapCount = 0
        self.iterations = 0
        self.currentSources = {}
        #print("*Number of destinations " + str(len(self.destinations)))
        if self.k ==0:
            print("this part needs no facilities ")
            self.currentSources = {}
            return
        if self.k ==1:
            self.solveOneMedianProblem()
            return

        if len(self.currentSources) ==0:
            #print("Gotta seeed")
            currentKeys = random.sample(list(self.destinations), self.k)
            i = 1
        #self.currentSources = {}

            for k in currentKeys:
                dest = self.destinations.get(k)
                self.tabooList[k] = dest
                source = Source.Source(dest.x, dest.y, dest.id, i)
                i += 1
                self.currentSources[source.id] = source
        #print(" Initial Sources ")
 #       self.printCurrentSources()
        #print("Len of current sources" + str(len(self.currentSources)))
        currentKeys = []
        for s in self.currentSources:
            currentKeys.append(self.currentSources[s].destinationId)

        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)

        self.doCurrentAssignment(self.currentSources)
        wholeIteration = 0
        self.iterations = 0 # Number of times the whole process is repeated

        self.bothSwap = True
        self.globalSwap = True
        #globalIteration = 0
        while (self.bothSwap):
            print("Working on Global Exchange")
            # print("Current Cost = " + str(self.calculateCurrentCost()))

            self.iterations+=1
            while (self.globalSwap):
                # print("Global swap # " + str(globalIteration))
                self.globalSwap = self.singleGlobalStep()
                if self.globalSwap:
                    self.globalSwapCount+=1
                # print("Current Cost = " + str(self.calculateCurrentCost()))



            self.doCurrentAssignment(self.currentSources)
            globalSources = dict(self.currentSources)
            globalCost = self.calculateCurrentCost()
            print("Global cost " + str(globalCost))
            print("Working on Local Exchange")
            localMinCost = globalCost
            self.bothSwap = False
            for s in self.currentSources:
                # print("Examining spurce " + str(s))
                source = self.currentSources[s]
                localSources = dict(self.currentSources)
                backUpMapping = {}
                for d in self.destinations:
                    backUpMapping[d] = self.currentDestinationToSourceMapping[d]
                backUpInverseMapping = {}
                for d in self.destIdToSourceId:
                    backUpInverseMapping[d] = self.destIdToSourceId[d]
                # print("old source should be " + str(self.currentSources.get(s).destinationId))
                for dest in source.destinations:
                    source = self.currentSources[s]
                    newSource = Source.Source(dest.x, dest.y, dest.id, s)
                    localSources[s] = Source.Source(dest.x, dest.y, dest.id, s)
                    self.handleSwapAssignments(source, newSource, localSources)

                    # self.iterations += 1
                    self.doCurrentAssignment(localSources)
                    localCost = self.calculateCurrentCost()
                    if localCost < localMinCost:
                        self.localSwapCount += 1
                        localMinCost = localCost
                        oldS = self.currentSources[s]
                        self.currentSources[s] = localSources[s]
                        self.handleSwapAssignments(oldS, localSources[s], self.currentSources)
                        # print("Changing to " + str(localCost))
                        # self.currentSources = dict(localSources)
                        # print("Local sources dest id ")
                        # self.doCurrentAssignment(self.currentSources)
                        # self.doCurrentAssignment(localSources)

                        # for s in localSources:
                        # self.currentSources[s] = localSources[s]
                        backUpMapping = {}
                        for d in self.destinations:
                            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
                        backUpInverseMapping = {}
                        for d in self.destIdToSourceId:
                            backUpInverseMapping[d] = self.destIdToSourceId[d]

                        self.destIdToSourceId = {}
                        for s in self.currentSources:
                            self.currentSources[s].destinations = []
                            csource = localSources[s]
                            self.destIdToSourceId[csource.destinationId] = s

                        for d in self.destinations:
                            did = self.currentDestinationToSourceMapping[d]
                            sourceid = self.destIdToSourceId[did]
                            self.currentSources.get(sourceid).destinations.append(self.destinations.get(d))

                        # self.doCurrentAssignment(self.currentSources)

                    else:
                        self.currentDestinationToSourceMapping = {}
                        for d in self.destinations:
                            self.currentDestinationToSourceMapping[d] = backUpMapping[d]
                        self.destIdToSourceId = {}
                        for d in self.destIdToSourceId:
                            self.destIdToSourceId[d] = backUpInverseMapping[d]

            # wholeIteration += 1
            if self.compareSources(globalSources, self.currentSources):
                self.doCurrentAssignment(self.currentSources)
                self.bothSwap = True
            else:
                self.currentSources = dict(globalSources)
                self.doCurrentAssignment(self.currentSources)

        # print(" NO IMPROVEMENT: EXTERMINATE")


    def griaStuffGlobal(self):
        self.localSwapCount = 0
        self.globalSwapCount = 0
        self.iterations = 0
        if len(self.currentSources) == 0:
            # print("Gotta seeed")
            currentKeys = random.sample(list(self.destinations), self.k)
            i = 1
            # self.currentSources = {}

            for k in currentKeys:
                dest = self.destinations.get(k)
                self.tabooList[k] = dest
                source = Source.Source(dest.x, dest.y, dest.id, i)
                i += 1
                self.currentSources[source.id] = source
        # print(" Initial Sources ")
        #       self.printCurrentSources()
        # print("Len of current sources" + str(len(self.currentSources)))
        currentKeys = []
        for s in self.currentSources:
            currentKeys.append(self.currentSources[s].destinationId)

        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)

        self.doCurrentAssignment(self.currentSources)
        self.iterations = 0  # Number of times the whole process is repeated

        self.bothSwap = True
        self.globalSwap = True
        # globalIteration = 0

        while (self.globalSwap):
            # print("Global swap # " + str(globalIteration))
            self.globalSwap = self.singleGlobalStepParallel()
            if self.globalSwap:
                self.globalSwapCount += 1
                # print("Current Cost = " + str(self.calculateCurrentCost()))

        self.doCurrentAssignment(self.currentSources)
        print("Number of succedsdul global swaps " + str(self.globalSwapCount))
        
        
    def findBestLocalDestination(self, sourceid):
        source = self.currentSources.get(sourceid)
        #print("Finding the optimal local replacement for " + str(sourceid) + "number of destination s" + str(len(source.destinations)))
        source  =self.currentSources.get(sourceid)
        numOfProcesses = 5
        processDestinationDictionary = {}
        manager = multiprocessing.Manager()
        p=0
        return_dict = manager.dict()
        if len(source.destinations) < numOfProcesses:
            numOfProcesses = len(source.destinations)
        for d in source.destinations:
            procId = p%numOfProcesses
            p+=1
            if processDestinationDictionary.get(procId) is None:
                processDestinationDictionary[procId] = []
                processDestinationDictionary[procId].append(d)
            else:
                processDestinationDictionary[procId].append(d)
        
        procs = []
        if __name__ == __name__:
            for i in range(numOfProcesses):
                swaps = 0
                #print("number of destinationns " + str(len(processDestinationDictionary.get(i))))
                p = multiprocessing.Process(target=self.swapTheseSources,args=(sourceid,processDestinationDictionary.get(i), i, return_dict, swaps))
                procs.append(p)
                p.start()
                # print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                # p.join()
            
            for p in procs:
                p.join()
        minCost = sys.maxsize
        # dropOptima = {}
        idToUpdate = -1
        for k in return_dict:
            myMin = return_dict.get(k)[0]
            self.localSwapCount+= return_dict.get(k)[2]
            if minCost > myMin:
                minCost = myMin
                idToUpdate = return_dict.get(k)[1]
        #print("Updating sources dest id from " + str(source.destinationId) +  "to " + str(idToUpdate))
        dest = self.destinations.get(idToUpdate)
        oldSource = self.currentSources[sourceid]
        self.currentSources[sourceid] =Source.Source(dest.x, dest.y, dest.id, sourceid)
        self.handleSwapAssignments(oldSource, self.currentSources[sourceid], self.currentSources)
        
    def swapTheseSources(self, sourceid, destinationList, i, return_dict, swaps ):
        if len(destinationList)==1 and self.currentSources[sourceid].destinationId == destinationList[0] :
            cost = self.calculateCurrentCost()
            source = self.currentSources[sourceid]
            selectedDest = self.destinations.get(source.destinationId)
            return_dict[i] = [cost, selectedDest.id]
            return
        localSources = dict(self.currentSources)
        backUpMapping = {}
        for d in self.destinations:
            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
        backUpInverseMapping = {}
        for d in self.destIdToSourceId:
            backUpInverseMapping[d] = self.destIdToSourceId[d]
        localMinCost = sys.maxsize
        source = self.currentSources[sourceid]
        selectedDest = self.destinations.get(source.destinationId)
        for dest in destinationList:
            newSource =  Source.Source(dest.x, dest.y, dest.id, sourceid)
            localSources[sourceid] = Source.Source(dest.x, dest.y, dest.id, sourceid)
            self.handleSwapAssignments(source, newSource, localSources)
            # self.iterations += 1
            #self.doCurrentAssignment(localSources)
            localCost = self.calculateCurrentCost()
            if localCost < localMinCost:
                #print(" swapping ")
                swaps +=1
                
                localMinCost = localCost
                selectedDest = dest
            self.currentDestinationToSourceMapping = {}
            for d in self.destinations:
                self.currentDestinationToSourceMapping[d] = backUpMapping[d]
            self.destIdToSourceId = {}
            for d in self.destIdToSourceId:
                self.destIdToSourceId[d] = backUpInverseMapping[d]
        #print("I was actually helpful " + str(len(destinationList)))
        #if selectedDest.id != source.destinationId:
            #print("WIN\n\n\n")
        return_dict[i] = [localMinCost, selectedDest.id, swaps]

    def griaStuffParallel(self):
        self.localSwapCount = 0
        self.globalSwapCount = 0
        self.iterations = 0
        self.currentSources = {}
        # print("*Number of destinations " + str(len(self.destinations)))
        if self.k == 0:
            print("this part needs no facilities ")
            self.currentSources = {}
            return
        if self.k == 1:
            self.solveOneMedianProblem()
            return
    
        if len(self.currentSources) == 0:
            # print("Gotta seeed")
            currentKeys = random.sample(list(self.destinations), self.k)
            i = 1
            # self.currentSources = {}
        
            for k in currentKeys:
                dest = self.destinations.get(k)
                self.tabooList[k] = dest
                source = Source.Source(dest.x, dest.y, dest.id, i)
                i += 1
                self.currentSources[source.id] = source
        # print(" Initial Sources ")
        #       self.printCurrentSources()
        # print("Len of current sources" + str(len(self.currentSources)))
        currentKeys = []
        for s in self.currentSources:
            currentKeys.append(self.currentSources[s].destinationId)
    
        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)
    
        self.doCurrentAssignment(self.currentSources)
        wholeIteration = 0
        self.iterations = 0  # Number of times the whole process is repeated
    
        self.bothSwap = True
    
        # globalIteration = 0
        while (self.bothSwap):
            print("Working on Global Exchange")
            # print("Current Cost = " + str(self.calculateCurrentCost()))
        
            self.iterations += 1
            while (self.globalSwap):
                # print("Global swap # " + str(globalIteration))
                self.globalSwap = self.singleGlobalStepParallel()
                if self.globalSwap:
                    self.globalSwapCount += 1
            print("Current Cost = " + str(self.calculateCurrentCost()))
        
            self.doCurrentAssignment(self.currentSources)
            self.globalSwap = True
            globalSources = dict(self.currentSources)
            globalCost = self.calculateCurrentCost()
            print("Global cost " + str(globalCost))
            print("Working on Local Exchange")
            localMinCost = globalCost
            self.bothSwap = False
            for s in self.currentSources:
                # print("Examining spurce " + str(s))
                source = self.currentSources[s]
                localSources = dict(self.currentSources)
                backUpMapping = {}
                for d in self.destinations:
                    backUpMapping[d] = self.currentDestinationToSourceMapping[d]
                backUpInverseMapping = {}
                for d in self.destIdToSourceId:
                    backUpInverseMapping[d] = self.destIdToSourceId[d]
                self.findBestLocalDestination(s)
                # print("old source should be " + str(self.currentSources.get(s).destinationId))
        
            # wholeIteration += 1
            if self.compareSources(globalSources, self.currentSources):
                self.doCurrentAssignment(self.currentSources)
                self.bothSwap = True
            else:
                self.currentSources = dict(globalSources)
                self.doCurrentAssignment(self.currentSources)
            if globalCost == self.calculateCurrentCost():
                self.bothSwap = False

    def griaStuffLocal(self):
        self.localSwapCount = 0
        self.globalSwapCount = 0
        self.iterations = 0
        if len(self.currentSources) == 0:
            # print("Gotta seeed")
            currentKeys = random.sample(list(self.destinations), self.k)
            i = 1
            # self.currentSources = {}

            for k in currentKeys:
                dest = self.destinations.get(k)
                self.tabooList[k] = dest
                source = Source.Source(dest.x, dest.y, dest.id, i)
                i += 1
                self.currentSources[source.id] = source
        # print(" Initial Sources ")
        #       self.printCurrentSources()
        # print("Len of current sources" + str(len(self.currentSources)))
        currentKeys = []
        for s in self.currentSources:
            currentKeys.append(self.currentSources[s].destinationId)

        complementKeys = []
        for d in self.destinations:
            if d not in currentKeys:
                complementKeys.append(d)

        self.doCurrentAssignment(self.currentSources)
        wholeIteration = 0
        self.iterations = 0  # Number of times the whole process is repeated

        self.bothSwap = True
        self.globalSwap = False
        # globalIteration = 0
        while (self.bothSwap):
            print("Local iteration :" + str(self.iterations))
            # print("Working on Global Exchange")
            # print("Current Cost = " + str(self.calculateCurrentCost()))

            self.iterations += 1
            while (self.globalSwap):
                # print("Global swap # " + str(globalIteration))
                self.globalSwap = self.singleGlobalStep()
                if self.globalSwap:
                    self.globalSwapCount += 1
                # print("Current Cost = " + str(self.calculateCurrentCost()))

            self.doCurrentAssignment(self.currentSources)
            globalSources = dict(self.currentSources)
            globalCost = self.calculateCurrentCost()
            # print("Global cost " + str(globalCost))
            # print("Working on Local Exchange")
            localMinCost = globalCost
            self.bothSwap = False
     
            for s in self.currentSources:
                #print("Examining spurce " + str(s))
                source = self.currentSources[s]
                localSources = dict(self.currentSources)
                backUpMapping = {}
                for d in self.destinations:
                    backUpMapping[d] = self.currentDestinationToSourceMapping[d]
                backUpInverseMapping = {}
                for d in self.destIdToSourceId:
                    backUpInverseMapping[d] = self.destIdToSourceId[d]
                # print("old source should be " + str(self.currentSources.get(s).destinationId))
                #print("find best local destination ")
                self.findBestLocalDestination(s)
               

            #wholeIteration += 1
            if self.compareSources(globalSources, self.currentSources):
                self.doCurrentAssignment(self.currentSources)
                self.bothSwap = True
            else:
                self.currentSources = dict(globalSources)
                self.doCurrentAssignment(self.currentSources)
            if globalCost == self.calculateCurrentCost():
                self.bothSwap = False

        # print(" NO IMPROVEMENT: EXTERMINATE")
        print("Total iterations " + str(self.iterations))
        print(" Local Iterations " + str(self.localSwapCount))
        print(" Global Iterations " + str(self.globalSwapCount))
        self.globalSwap = True
        self.bothSwap = True
        self.localSwap = False

    def compareSources(self, dict1, dict2):
        arrayDictIds2 = []
        for s in dict2:
            arrayDictIds2.append(dict2[s].destinationId)
        change = False
        for s in dict1:
            destid = dict1[s].destinationId
            if destid not in arrayDictIds2:
                change = True
                break
        #print("am I diff " + str(change))
        return change

    def initializeCurrentSources(self, sources):
        self.currentSources = dict(sources)
        #self.current_r_value = self.calculateCurrentCost()

    def saveResultsToDatabase(self):
        self.sourceDao.createSourceTable('gria')
        self.sourceDao.populateSourceTable(self.minSources,'gria')
        self.sourceDao.createCatchmentAreas(self.minSources,'gria')

    def saveDestToSourceMapping(self,cnt,name):
        self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations,cnt, name)


    def createSitationInputFile(self, fileName):
        data = []
        for k in self.destinations:
            bg = self.destinations[k]
            row= [bg.id, bg.x, bg.y, bg.demand, bg.demand, 0]
            data.append(row)

        with open(fileName, 'w') as f:
            # print('wrting to csv')
            writer = csv.writer(f)
            writer.writerows(data)

    def calculateAverageDistanceCost(self):
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
        print(len(self.currentSources))

        for s in self.currentSources:
            source = self.currentSources.get(s)
            print("Number of destinations for this source")
            print(len(source.destinations))
            ncheck += len(source.destinations)
            for dest in source.destinations:
                source.totalDemand += dest.demand
                weightedAverage += (self.distanceMap[source.destinationId][dest.id])*dest.weight
                disAverage += self.distanceMap[source.destinationId][dest.id]
            for dest in source.destinations:
                sourceAverage += (self.distanceMap[source.destinationId][dest.id])*(dest.demand/source.totalDemand)
        n = len(self.destinations)
        print("n = " + str(n))
        print("ncheck = " + str(ncheck))
        print("Distance total " + str(disAverage))
        print("Weighted Distance total " + str(weightedAverage))
        print("Source Weighted Distance total " + str(sourceAverage))
        print("*******\n\n")
        print("Distance total " + str(disAverage/n))
        print("Weighted Distance total " + str(weightedAverage/n))
        print("Source Weighted Distance total " + str(sourceAverage/n))


    def createSourcesFromEPP(self):
        destinationIds = self.destinationDao.getEPPSolution()
        i = 1
        eppSources = {}
        for d in destinationIds:
            dest = self.destinations.get(d)
            newSource = Source.Source(dest.x, dest.y, dest.id, i)
            eppSources[i] = newSource
            i = i +1
        return eppSources


    def pathRelinkingProperExchange(self):
        currentK = len(self.currentSources)
        print("Gotta reduce it to " + str(self.k))
        destPool = []
        for s in self.currentSources:
            source = self.currentSources.get(s)
            destPool.append(source.destinationId)
        currentKeys = random.sample(destPool, self.k)
        self.allSources = dict(self.currentSources)
        self.currentSources = {}
        i = 1

        for k in currentKeys:
            dest = self.destinations.get(k)
            self.tabooList[k] = dest
            source = Source.Source(dest.x, dest.y, dest.id, i)
            i += 1
            self.currentSources[source.id] = source
        complementKeys = []
        for d in destPool:
            if d not in currentKeys:
                complementKeys.append(d)
        self.doCurrentAssignment(self.currentSources)
        self.current_r_value = self.calculateCurrentCost()
        terminationCondition = False
        iterations = 0
        while terminationCondition == False and iterations < self.maxIterations:
            print("iteration " + str(iterations))
            currentSourcesBackUp = dict(self.currentSources)
            v1_sources = dict(self.currentSources)
            r_min_b = self.current_r_value
            bWinner = {}
            for comp in complementKeys:
                if self.tabooList.get(comp) is None:
                    print("Trying to Adding " + str(comp))
                    dest_b = self.destinations.get(comp)
                    vertex_k = -1
                    delta_min = sys.maxsize
                    for vertex in v1_sources:
                        vj = v1_sources.get(vertex)
                        self.currentSources.update({vertex: Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex)})
                        self.doCurrentAssignment(self.currentSources)
                        delta_bj = self.calculateCurrentCost() - self.current_r_value
                        self.currentSources = dict(currentSourcesBackUp)
                        if delta_bj < 0 and delta_bj < delta_min:
                            delta_min = delta_bj
                            vertex_k = vertex

                    if vertex_k != -1:
                        print("Found one to replaxe "+ str(self.currentSources.get(vertex_k).destinationId))
                        toReplace = self.currentSources[vertex_k]
                        self.currentSources.update({vertex_k: Source.Source(dest_b.x, dest_b.y, dest_b.id, vertex_k)})
                        self.doCurrentAssignment(self.currentSources)
                        if self.calculateCurrentCost() < r_min_b:
                            r_min_b = self.calculateCurrentCost()
                            bWinner = dict(self.currentSources)
                        self.currentSources.update({vertex_k: toReplace})
                        self.doCurrentAssignment(self.currentSources)

            if r_min_b < self.current_r_value:
                print("r current defeated !!!")
                print("r_current " + str(self.current_r_value) + " r_min_b " + str(r_min_b))
                self.currentSources = dict(bWinner)
                self.current_r_value = r_min_b
                currentKeys = []
                for s in self.currentSources:
                    currentKeys.append(self.currentSources.get(s).destinationId)
                    self.tabooList.update({self.currentSources.get(s).destinationId: self.destinations.get(
                        self.currentSources.get(s).destinationId)})
                complementKeys = []
                for d in self.destinations:
                    if d not in currentKeys:
                        complementKeys.append(d)
                iterations += 1
            else:
                self.doCurrentAssignment(self.currentSources)
                terminationCondition = True
                print(" Ending Program==>  No improvement possible ")
    def assignTheseDestinations(self, tempDict, homelessDestinations):
        for dest in homelessDestinations:
            d = dest.id
            self.currentDestinationToSourceMapping[d] = self.pickMinSource(d, tempDict)

    def evaluateTheseSourcesForDeletion(self, myCanditates, i, returnDict):
        tempDict = dict(self.currentSources)
        currentCost = self.calculateCurrentCost()
        dropOptima = {}
        idToUpdate = -1
        dropCost = sys.maxsize
        backUpMapping = {}
        for d in self.destinations:
            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
        for s in myCanditates:
            removedSource = self.currentSources[s]
            del tempDict[s]
            for d in removedSource.destinations:
                self.currentDestinationToSourceMapping[d.id] = self.pickMinSource(d.id, tempDict)
                # self.doCurrentAssignment(tempDict)
                # self.doCurrentAssignment(tempDict)
            tempCost = self.calculateCurrentCost()
            if dropCost > tempCost:
                dropCost = tempCost
                idToUpdate = s
                dropOptima = dict(tempDict)
            tempDict[s] = removedSource
            self.currentDestinationToSourceMapping = {}
            for d in backUpMapping:
                self.currentDestinationToSourceMapping[d] = backUpMapping[d]

        returnDict[i] = [dropOptima, dropCost, idToUpdate]

    def greedyRemoval(self):
        print("Number of sources currently " + str(len(self.currentSources)))
        print("Gotta reduce it to " + str(self.k))
        self.doCurrentAssignment(self.currentSources)
        while (len(self.currentSources)>self.k):
            print("One more deletion")
            numOfProcesses = 5
            processSourceDictionary = {}
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            for s in self.currentSources:
                procId = s % numOfProcesses
                if processSourceDictionary.get(procId) is None:
                    processSourceDictionary[procId] = {}
                processSourceDictionary[procId][s] = self.currentSources.get(s)
            procs = []
            if __name__ == __name__:
                for i in range(numOfProcesses):
                    p = multiprocessing.Process(target=self.evaluateTheseSourcesForDeletion,
                                                args=(processSourceDictionary[i], i, return_dict))
                    procs.append(p)
                    p.start()
                    # print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                    # p.join()

                for p in procs:
                    p.join()
            dropCost = sys.maxsize
            #dropOptima = {}
            idToUpdate = -1
            for k in return_dict:
                myMin = return_dict.get(k)[1]
                if dropCost > myMin:
                    dropCost = myMin
                    #dropOptima = return_dict.get(k)[0]
                    idToUpdate = return_dict.get(k)[2]
            print("Deleting " + str(idToUpdate) + ": " + str(self.currentSources.get(idToUpdate).destinationId))
            del self.currentSources[idToUpdate]
            self.doCurrentAssignment(self.currentSources)
            print("Current Number of sources " + str(len(self.currentSources)))





    def pathRelinking(self):
        print("\n\n ****************************************** REDUCTION THROUGH PARALLEL GRIA ***********************************\n\n")
        currentK = len(self.currentSources)
        print("Current facilities "+ str(currentK))
        print("Gotta reduce it to " + str(self.k))
        destPool = []
        for s in self.currentSources:
            source = self.currentSources.get(s)
            destPool.append(source.destinationId)
        currentKeys =  random.sample(destPool, self.k)
        self.allSources = dict(self.currentSources)
        self.currentSources = {}
        i = 1
        for k in currentKeys:
            dest = self.destinations.get(k)
            self.tabooList[k] = dest
            source = Source.Source(dest.x, dest.y, dest.id, i)
            i += 1
            self.currentSources[source.id] = source
        complementKeys = []
        for d in destPool:
            if d not in currentKeys:
                complementKeys.append(d)
        self.doCurrentAssignment(self.currentSources)
        wholeIteration = 0
        self.iterations = 0  # Number of times the whole process is repeated

        self.bothSwap = True
        self.globalSwap = False
        # globalIteration = 0
        while (self.bothSwap):
            print("iteration :" + str(self.iterations))
            print("Number of current sources " + str(len(self.currentSources)))
            self.globalSwap = True
            self.iterations += 1
            while (self.globalSwap):
                # print("Global swap # " + str(globalIteration))
                self.globalSwap = self.singleGlobalStepParallel(complementKeys)
                if self.globalSwap:
                    self.globalSwapCount += 1
                # print("Current Cost = " + str(self.calculateCurrentCost()))

            self.doCurrentAssignment(self.currentSources)
            globalSources = dict(self.currentSources)
            globalCost = self.calculateCurrentCost()
            print("Global cost " + str(globalCost))
            print("Working on Local Exchange")
            localMinCost = globalCost
            self.bothSwap = False
            for s in self.currentSources:
                # print("Examining spurce " + str(s))
                source = self.currentSources[s]
                localSources = dict(self.currentSources)
                backUpMapping = {}
                for d in self.destinations:
                    backUpMapping[d] = self.currentDestinationToSourceMapping[d]
                backUpInverseMapping = {}
                for d in self.destIdToSourceId:
                    backUpInverseMapping[d] = self.destIdToSourceId[d]
                # print("old source should be " + str(self.currentSources.get(s).destinationId))
                for dest in source.destinations:
                    source = self.currentSources[s]
                    newSource = Source.Source(dest.x, dest.y, dest.id, s)
                    localSources[s] = Source.Source(dest.x, dest.y, dest.id, s)
                    self.handleSwapAssignments(source, newSource, localSources)

                    # self.iterations += 1
                    self.doCurrentAssignment(localSources)
                    localCost = self.calculateCurrentCost()
                    if localCost < localMinCost:
                        self.localSwapCount += 1
                        localMinCost = localCost
                        oldS = self.currentSources[s]
                        self.currentSources[s] = localSources[s]
                        self.handleSwapAssignments(oldS, localSources[s], self.currentSources)
                        # print("Changing to " + str(localCost))
                        # self.currentSources = dict(localSources)
                        # print("Local sources dest id ")
                        # self.doCurrentAssignment(self.currentSources)
                        # self.doCurrentAssignment(localSources)

                        # for s in localSources:
                        # self.currentSources[s] = localSources[s]
                        backUpMapping = {}
                        for d in self.destinations:
                            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
                        backUpInverseMapping = {}
                        for d in self.destIdToSourceId:
                            backUpInverseMapping[d] = self.destIdToSourceId[d]

                        self.destIdToSourceId = {}
                        for s in self.currentSources:
                            self.currentSources[s].destinations = []
                            csource = localSources[s]
                            self.destIdToSourceId[csource.destinationId] = s

                        for d in self.destinations:
                            did = self.currentDestinationToSourceMapping[d]
                            sourceid = self.destIdToSourceId[did]
                            self.currentSources.get(sourceid).destinations.append(self.destinations.get(d))

                        # self.doCurrentAssignment(self.currentSources)

                    else:
                        self.currentDestinationToSourceMapping = {}
                        for d in self.destinations:
                            self.currentDestinationToSourceMapping[d] = backUpMapping[d]
                        self.destIdToSourceId = {}
                        for d in self.destIdToSourceId:
                            self.destIdToSourceId[d] = backUpInverseMapping[d]

            # wholeIteration += 1
            if self.compareSources(globalSources, self.currentSources):
                self.doCurrentAssignment(self.currentSources)
                self.bothSwap = True
            else:
                self.currentSources = dict(globalSources)
                self.doCurrentAssignment(self.currentSources)

        # print(" NO IMPROVEMENT: EXTERMINATE")

    def handleSwapAssignments(self, oldSource, newSource, localSources):
        if oldSource.destinationId != newSource.destinationId:
            newSource.destinations =[]
            #print("Handling swaps")
            #print("===> Allowed Local sources dest id ")
            allowed = []
            cs = []
            for sl in localSources:
                #print(" did for " + str(sl) + str(":") + str(localSources.get(sl).destinationId))
                allowed.append(localSources.get(sl).destinationId)
                cs.append(self.currentSources.get(sl).destinationId)
            #print(allowed)
            #print(cs)
            #print("old == "+str(oldSource.destinationId))
            self.destIdToSourceId = {}
            for d in self.destinations:
                #print("\n********\ndest " + str(d))
                currentSourceDid = self.currentDestinationToSourceMapping[d]
                if  currentSourceDid  == oldSource.destinationId:
                    #print("finding new source ")
                    minSource = self.pickMinSourceObject(d,localSources)
                    self.currentDestinationToSourceMapping[d] = minSource.destinationId
                    self.destIdToSourceId[self.currentDestinationToSourceMapping[d]] = minSource.id
                    if self.currentDestinationToSourceMapping[d] not in allowed:
                        print(allowed)
                        print("new How !!!")
                        print(str(self.currentDestinationToSourceMapping[d]))
                        exit(0)
                    #print("foubnd!")
                else:
                    #print("safe, but is the new source better ")
                    if self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(currentSourceDid)) > self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), newSource):
                        #print("yess!")
                        self.currentDestinationToSourceMapping[d] = newSource.destinationId
                        self.destIdToSourceId[self.currentDestinationToSourceMapping[d]] = newSource.id
                    if self.currentDestinationToSourceMapping[d] not in allowed:
                        print(allowed)
                        print(" better How !!!")
                        print("purana " + str(cs))
                        print("New " + str(newSource.destinationId))
                        print("old;s id "+ str(oldSource.destinationId))
                        print("curemt " +str(currentSourceDid))
                        print(str(self.currentDestinationToSourceMapping[d]))
                        exit(0)
    def singleGlobalStepReduced(self, complementKeys):
        currentCost = self.calculateCurrentCost()
        tempDict = dict(self.currentSources)
        dropOptima = {}
        idToUpdate = -1
        dropCost = sys.maxsize
        ## DROP PART
        for s in self.currentSources:
            removedSource = self.currentSources[s]
            homelessDestinations = removedSource.destinations
            del tempDict[s]
            self.assignTheseDestinations(tempDict, homelessDestinations)
            #self.doCurrentAssignment(tempDict)
            tempCost = self.calculateCurrentCost()
            if dropCost > tempCost:
                dropCost = tempCost
                idToUpdate = s
                dropOptima = dict(tempDict)
            tempDict[s] = removedSource

        ## ADD PART
        addOptima = {}
        tempDict = dict(dropOptima)
        addCost = sys.maxsize
        self.doCurrentAssignment(dropOptima)
        for d in complementKeys:
            dest = self.destinations[d]
            newSource = Source.Source(dest.x, dest.y, dest.id, idToUpdate)
            tempDict[idToUpdate] = newSource
            self.doCurrentAssignment(tempDict)
            tempCost = self.calculateCurrentCost()
            if addCost > tempCost:
                addCost = tempCost
                addOptima = dict(tempDict)
            del tempDict[idToUpdate]
        if addCost - currentCost < 0 :
            self.currentSources = dict(addOptima)
            self.doCurrentAssignment(self.currentSources)
            return True
        else:
            self.doCurrentAssignment(self.currentSources)
            return False


    def assignDestinationsToNewSource(self, newSource):
        newDest = self.destinations.get(newSource.destinationId)
        for d in self.destinations:
            currentSource = self.destinations.get(self.currentDestinationToSourceMapping[d])
            dest = self.destinations.get(d)
            currentDistance = self.util.calculateDistanceBetweenDestinationsWeighted(currentSource, dest )
            newDistance = self.util.calculateDistanceBetweenDestinationsWeighted(newDest, dest)
            if newDistance < currentDistance:
                self.currentDestinationToSourceMapping[d] = newDest
                newSource.destinations.append(dest)
                currentSource.destinations.remove(dest)



    def evaluateTheseDestinationsForAddition(self, myCandidates, i, returnDict, dropOptima, idToUpdate):
        addOptima = {}
        tempDict = dict(dropOptima)
        addCost = sys.maxsize
        backUpMapping = {}
        for d in self.destinations:
            backUpMapping[d] = self.currentDestinationToSourceMapping[d]
        backUpInverseMapping = {}
        for d in self.destIdToSourceId:
            backUpInverseMapping[d] = self.destIdToSourceId[d]
        for d in myCandidates:
            if self.checkCurrentSources(d, dropOptima):
                dest = self.destinations[d]
                newSource = Source.Source(dest.x, dest.y, dest.id, idToUpdate)
                tempDict[idToUpdate] = newSource
                for d in self.destinations:
                    dest = self.destinations.get(d)
                    currentSourceDid = self.currentDestinationToSourceMapping[d]
                    sourceId = self.destIdToSourceId[currentSourceDid]
                    source = self.currentSources.get(sourceId)
                    currentDistance = self.util.calculateDistanceBetweenDestinations(dest, source)
                    newDistance = self.util.calculateDistanceBetweenDestinations(dest, newSource)
                    if newDistance < currentDistance:
                        self.currentDestinationToSourceMapping[d] = newSource.destinationId

                # self.doCurrentAssignment(tempDict)
                tempCost = self.calculateCurrentCost()
                if addCost > tempCost:
                    addCost = tempCost
                    addOptima = dict(tempDict)
                del tempDict[idToUpdate]
                self.currentDestinationToSourceMapping = {}
                for d in self.destinations:
                    self.currentDestinationToSourceMapping[d] = backUpMapping[d]
        returnDict[i] = [addOptima, addCost]

    def pickMinSourceObject(self, destination, sourceDict):

        min = sys.maxsize
        minSource = 1
        minsid = -1
        for source in sourceDict:
            sid = sourceDict[source].id
            s = sourceDict[source].destinationId
            if destination == s:
                minSource = s
                minsid = sid
                break
            else:
                if self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(destination)) < min:
                    min = self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(destination))
                    minSource = s
                    minsid = sid
        # print("closest source "+ str(minsid))
        sourceToUpdate = sourceDict.get(minsid)
        sourceDict.get(minsid).destinations.append(self.destinations.get(destination))
        return sourceToUpdate

    def singleGlobalStepParallel(self, complementKeys = []):
        currentCost = self.calculateCurrentCost()
        
        #print("current cosrt " + str(currentCost))
        ## DROP PART
        numOfProcesses = 5
        processSourceDictionary = {}
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        for s in self.currentSources:
            procId = s%numOfProcesses
            if processSourceDictionary.get(procId) is None:
                processSourceDictionary[procId] = {}
            processSourceDictionary[procId][s] = self.currentSources.get(s)
        procs = []
        if __name__ ==__name__:
            for i in range(numOfProcesses):
                p = multiprocessing.Process(target=self.evaluateTheseSourcesForDeletion, args=(processSourceDictionary[i],i,return_dict))
                procs.append(p)
                p.start()
                #print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                #p.join()


            for p in procs:
                p.join()
        dropCost = sys.maxsize
        dropOptima ={}
        idToUpdate = -1
        for k in return_dict:
            myMin  = return_dict.get(k)[1]
            if dropCost > myMin:
                dropCost = myMin
                dropOptima = return_dict.get(k)[0]
                idToUpdate = return_dict.get(k)[2]

        #print(" Dropping source " + str(idToUpdate) + " from current sources "+ "destination id " + str(self.currentSources.get(idToUpdate).destinationId))
        self.doCurrentAssignment(dropOptima)
        processDestinationsDictionary = {}
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        for d in self.destinations:
            procId = d%numOfProcesses
            if processDestinationsDictionary.get(procId) is None:
                processDestinationsDictionary[procId] = []
            processDestinationsDictionary[procId].append(d)
        procs = []
        if __name__ == __name__:
            for i in range(numOfProcesses):
                p = multiprocessing.Process(target=self.evaluateTheseDestinationsForAddition,args=(processDestinationsDictionary[i], i, return_dict, dropOptima, idToUpdate))
                procs.append(p)
                p.start()

                #print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processDestinationsDictionary[i])))
                # p.join()

            for p in procs:
                p.join()
        addOptima = {}
        tempDict = dict(dropOptima)
        addCost = sys.maxsize
        for k in return_dict:
            myMin  = return_dict.get(k)[1]
            if addCost > myMin:
                addCost = myMin
                addOptima = return_dict.get(k)[0]

        if addCost - currentCost < 0:
            #print(" Adding source " + str(idToUpdate) + " from current sources " + "destination id " + str(addOptima.get(idToUpdate).destinationId))
            #print("new cosrt " + str(addCost))
            self.currentSources = dict(addOptima)
            self.doCurrentAssignment(self.currentSources)
            return True
        else:
            self.doCurrentAssignment(self.currentSources)
            return False




