import sys
import collections
import random
from Cofig import  params
from DAOs import SourceDAO
from DAOs import DestinationDAO
from Model import Source
from Model import Destination
import Utilities as util
from Distribution import  NormalityTester
class Maranzana:
    def __init__(self, k, distType):
        self.k = k
        self.distType = distType
        self.maxIterations = 100
        #self.n = n
        self.currentSources = {}
        self.newSources = {}
        self.minSources = {}
        self.destinations = {}
        self.sourceIdToDesinationIdMap = {}
        self.distanceMap = {}
        self.sourceDao = SourceDAO.SourceDAO(k, distType,'Maranzana')
        self.destinationDao = DestinationDAO.DestinationDAO(distType)
        self.util = util.Utilities()
        self.weightMap = {}
        self.currentDestinationToSourceMapping = {} # destination to source (id only)
        self.maxPopulation = 1
        self.iterations =0
        self.totalDemandInTheRegion = 0
        self.parts = {}
        self.partToDestinationMap = {}

    # def initializeSources(self):
    #     results = self.sourceDao.initializeSources()
    #     count = 1
    #     for row in results:
    #         newSource = Source.Source(row['x'], row['y'], row['destinationid'])
    #         newSource.id = count
    #         self.sourceIdToDesinationIdMap[newSource.id] = row['destinationid']
    #         count += 1
    #         self.currentSources[newSource.id] = newSource

    def printCurrentSources(self):
        print("Printing current sources")
        for id in self.currentSources:
            source = self.currentSources[id]
            #print("Id = "+str(source.id))
            #print("X = "+str(source.x))
            #print("Y = "+str(source.y))
            #print("Destination Id = "+str(source.destinationId))

    def getAllDestinations(self):
        results = self.destinationDao.getAllSyntheticDestinations(self.distType)
        for row in results:
            newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
            self.totalDemandInTheRegion+= int(row['demand'])
            self.destinations[newDestination.id] = newDestination
        self.n = len(self.destinations)
        print("Number of destintions "+ str(self.n))
        #self.printAllDestinations()
    def printAllDestinations(self):
        for id in self.destinations:
            print("###########")
            destination = self.destinations[id]
            print("Replan Id = " + str(destination.id))
            print("X = " + str(destination.x))
            print("Y = " + str(destination.y))
            print("Demand= " + str(destination.demand))



    def buildDistanceMap(self):
        for d1 in self.destinations:
            self.distanceMap[d1] = {}
            dest1 = self.destinations[d1]
            for d2 in self.destinations:
                dest2 = self.destinations[d2]
                distance = self.util.calculateDistanceBetweenDestinations(dest1, dest2)
                self.distanceMap[d1][d2] = distance
        #self.printDistanceMap()

    def printDistanceMap(self):
        for d1 in self.distanceMap:
            for d2 in self.distanceMap[d1]:
                print("Distance between " + str(d1) + " and " + str(d2) + "=" + str(self.distanceMap[d1][d2])+ " weight = "+ str(self.weightMap[d1][d2]))

    def getMaxPopulation(self):
        max = 0
        for k in self.destinations:
            d = self.destinations.get(k)
            if max < d.demand:
                max = d.demand
        self.maxPopulation = max

        #return float(max)

    def populateWeightMap(self):
        self.getMaxPopulation()
        #print(str(self.getMaxPopulation()) + "--> max population")
        for d1 in self.distanceMap:
            self.weightMap[d1] = {}
            for d2 in self.distanceMap[d1]:
                dest2 = self.destinations[d2]
                self.weightMap[d1][d2] = self.distanceMap[d1][d2]*(dest2.demand/self.maxPopulation)
                #print(self.weightMap[d1][d2])
        self.printDistanceMap()


    def kMeansStuff(self):
        # Do kmeans stuff
        self.iterations = 0
        printFlag = False
        if len(self.currentSources) == 0:
            #print("Random selection")
            currentKeys = random.sample(list(self.destinations), self.k)
            i = 1
            self.currentSources = {}
            for k in currentKeys:
                dest = self.destinations.get(k)
                source = Source.Source(dest.x, dest.y, dest.id,i)
                #source.id = i
                i += 1
                self.currentSources[source.id] = source
        else:
            printFlag = True
            print("I already have sources")
        #print(" Initial Sources ")
        #self.printCurrentSources()
        terminationCondition = False
        itc = 0
        self.doCurrentAssignment()
        while not terminationCondition:
            if printFlag:
                print("itr " + str(itc) + "cost " + str(self.calculateCurrentCost()))
            #print("Iteration # "  + str(itc))
            self.calculateNewSources()

            terminationCondition = self.checkForTermination()
            #print(" termination Condition " + str(terminationCondition))
            if not terminationCondition:
                #print(" Not terminating ")
                self.currentSources = dict(self.newSources)
                self.newSources.clear()
                self.doCurrentAssignment()

            itc +=1
        #print("I should be here ")

    def kMeansStuffActual(self):
        # Do kmeans stuff
        self.iterations = 0
        printFlag = True
        if len(self.currentSources) == 0:
            # print("Random selection")
            currentKeys = random.sample(list(self.destinations), self.k)
            i = 1
            self.currentSources = {}
            for k in currentKeys:
                dest = self.destinations.get(k)
                source = Source.Source(dest.x, dest.y, dest.id, i)
                # source.id = i
                i += 1
                self.currentSources[source.id] = source
        else:
            printFlag = True
            print("I already have sources")
        # print(" Initial Sources ")
        # self.printCurrentSources()
        terminationCondition = False
        itc = 0
        self.doCurrentAssignmentActual()
        while not terminationCondition:
            #if printFlag:
                #print("itr " + str(itc) + "cost " + str(self.calculateCurrentCostActual()))
            # print("Iteration # "  + str(itc))
            self.calculateNewSourcesActual()

            terminationCondition = self.checkForTermination()
            # print(" termination Condition " + str(terminationCondition))
            if not terminationCondition:
                # print(" Not terminating ")
                self.currentSources = dict(self.newSources)
                self.newSources.clear()
                self.doCurrentAssignmentActual()

            itc += 1
        # print("I should be here ")

    def pickMinSource(self,destination):
        min = sys.maxsize
        minSource = 1
        minsid = -1
        for source in self.currentSources:
            sid = self.currentSources[source].id
            #print("hererre "+ str(sid))
            s = self.currentSources[source].destinationId
            if  self.distanceMap[s][destination] < min:
                min = self.distanceMap[s][destination]
                minSource = s
                minsid = sid
        #print("closest source "+ str(minsid))
        sourceToUpdate = self.currentSources.get(minsid)
        self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
        return minSource


    def pickMinSourceBasedOnDistance(self,destination):
        min = sys.maxsize
        minSource = 1
        minsid = -1
        for source in self.currentSources:
            sid = self.currentSources[source].id
            src = self.currentSources.get(source)
            #print("hererre "+ str(sid))
            s = self.currentSources[source].destinationId
            if  self.util.calculateDistanceBetweenDestinations(src, self.destinations.get(destination)) < min:
                min = self.util.calculateDistanceBetweenDestinations(src, self.destinations.get(destination))
                minSource = s
                minsid = sid
        #print("closest source "+ str(minsid))
        sourceToUpdate = self.currentSources.get(minsid)
        self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
        return minsid

    def doCurrentAssignment(self):
        for s in self.currentSources:
            source = self.currentSources.get(s)
            source.destinations = []
        for d in self.destinations:
            self.currentDestinationToSourceMapping[d] = self.pickMinSource(d)
        #print(" Done with current assignment")
        #print(" Total destinations = " +str(len(self.destinations)))
        #for s in self.currentSources:
            #print(" Number of destinations assigned to " + str(s) + " =  " +str(len(self.currentSources.get(s).destinations)))

    def doCurrentAssignmentActual(self):
        for s in self.currentSources:
            source = self.currentSources.get(s)
            source.destinations = []
        for d in self.destinations:
            self.currentDestinationToSourceMapping[d] = self.pickMinSourceBasedOnDistance(d)
        # print(" Done with current assignment")
        # print(" Total destinations = " +str(len(self.destinations)))
        # for s in self.currentSources:
        # print(" Number of destinations assigned to " + str(s) + " =  " +str(len(self.currentSources.get(s).destinations)))

    def calculateCurrentCost(self):
        cost = 0.0
        for d in self.currentDestinationToSourceMapping:
            s = self.currentDestinationToSourceMapping[d]
            cost += self.distanceMap[s][d]*(self.destinations.get(d).demand)
            #?? which should be used?
            #cost += self.distanceMap[s][d]
        return cost

    def calculateCurrentCostActual(self):
        cost = 0.0
        for d in self.currentDestinationToSourceMapping:
            s = self.currentDestinationToSourceMapping[d]
            source = self.currentSources.get(s)
            cost +=  self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), source)* (self.destinations.get(d).demand)
            # ?? which should be used?
            # cost += self.distanceMap[s][d]
        return cost

    def calculateNewSources(self):
        self.newSources = {}
        for s in self.currentSources:
            #print("Replacing: " + str(s))
            sizeForS = len(self.currentSources.get(s).destinations)
            eDis = 0
            newDis  = 0
            xCoord = 0.0
            yCoord = 0.0
            xCoordw = 0.0
            yCoordw = 0.0
            demandSum = 0
            for ds in self.currentSources.get(s).destinations:
                demandSum += ds.demand
                eDis += self.distanceMap[self.currentSources[s].destinationId][ds.id]
                xCoordw += float(ds.demand) * ds.x
                yCoordw += float(ds.demand) * ds.y
                xCoord += ds.x
                yCoord += ds.y

            if(xCoord!=0.0 and sizeForS != 0):
                xCoordw = (xCoordw/demandSum)
                yCoordw = (yCoordw/demandSum)
                xCoord = xCoord/sizeForS
                yCoord = yCoord/sizeForS
                #print("weighted =>" + str(xCoordw) + ", " + str(yCoordw))
                #print("Non weighted =>" + str(xCoord) + ", " + str(yCoord))
                cd = self.findClosestDestination(xCoordw, yCoordw)
            for ds in self.currentSources.get(s).destinations:
                newDis += self.distanceMap[cd.id][ds.id]
            if newDis < eDis:
                self.newSources[s] = Source.Source(cd.x, cd.y, cd.id, s)
            else:
                self.newSources[s] = self.currentSources[s]
            #print("newdis " + str(newDis) +" edis" + str(eDis))

    def calculateNewSourcesActual(self):
        self.newSources = {}
        for s in self.currentSources:
            # print("Replacing: " + str(s))
            sizeForS = len(self.currentSources.get(s).destinations)

            xCoord = 0.0
            yCoord = 0.0
            xCoordw = 0.0
            yCoordw = 0.0
            demandSum = 0
            for ds in self.currentSources.get(s).destinations:
                demandSum += ds.demand

                xCoordw += float(ds.demand) * ds.x
                yCoordw += float(ds.demand) * ds.y
                xCoord += ds.x
                yCoord += ds.y

            if (xCoord != 0.0 and sizeForS != 0):
                xCoordw = (xCoordw / demandSum)
                yCoordw = (yCoordw / demandSum)
                xCoord = xCoord / sizeForS
                yCoord = yCoord / sizeForS
                # print("weighted =>" + str(xCoordw) + ", " + str(yCoordw))
                # print("Non weighted =>" + str(xCoord) + ", " + str(yCoord))

            self.newSources[s] = Source.Source(xCoordw, yCoordw, -1, s)


    def findClosestDestination(self,x,y):
        tempDestination = Destination.Destination(-1, x,y,0 )
        #print(" FInd closest for " + str(x) + ", " + str(y))
        minDistance = sys.maxsize
        closestDest = None
        for d in self.destinations:
            distance =  self.util.calculateDistanceBetweenDestinations(self.destinations.get(d),tempDestination)
            if minDistance > distance:
                #print("UPDATING MIN DISTANCE " + str(d))
                minDistance = distance
                closestDest = self.destinations.get(d)
        return closestDest


    def checkForTermination(self):
        currentds = []
        newds = []
        for s in self.currentSources:
            currentds.append(self.currentSources.get(s).destinationId)
        for ns in self.newSources:
            newds.append(self.newSources.get(ns).destinationId)
        return set(currentds) == set(newds)

    def printMinSolution(self):
        print("Printing current sources")
        for id in self.minSources:
            source = self.minSources[id]
            # print("Id = "+str(source.id))
            # print("X = "+str(source.x))
            # print("Y = "+str(source.y))
            print("Destination Id = " + str(source.destinationId))


    def updateCostForMinSolution(self):
        for id in self.minSources:
            source = self.minSources[id]
            for d in source.destinations:
                source.cost += self.distanceMap[source.destinationId][d.id]
                source.x = self.destinations.get(source.destinationId).x
                source.y = self.destinations.get(source.destinationId).y

    def kMeansWithInitialSources(self, sourceDict):
        # Do kmeans stuff
        self.currentSources = dict(sourceDict)
        self.printCurrentSources()
        terminationCondition = False
        itc = 0
        while terminationCondition == False:
            #print("Iteration # "  + str(itc))
            self.doCurrentAssignment()
            self.calculateNewSources()
            terminationCondition = self.checkForTermination()

            if not terminationCondition:
                #print(" Not terminating ")
                self.currentSources = dict(self.newSources)
                self.newSources.clear()
                #print(" New sources  ")
                #self.printCurrentSources()
            itc +=1
            if itc > self.maxIterations:
                terminationCondition = True
        #print(" Final Sources ")
        #self.printCurrentSources()



    def getMaximalIntraClusterDistance(self):
        dk = 0
        for s in self.currentSources:
            source = self.currentSources.get(s)
            for d in source.destinations:
                for d1 in source.destinations:
                    if d1.id != d.id:
                        if self.util.calculateDistanceBetweenDestinations(d,d1) > dk:
                            dk = self.util.calculateDistanceBetweenDestinations(d,d1)
        return dk
    # Dunn Index
    def measureQualityDunn(self):
        dk = self.getMaximalIntraClusterDistance()
        mincij = sys.maxsize
        for s in self.currentSources:
            sourcei = self.currentSources.get(s)
            for s1 in self.currentSources:
                if s!=s1:
                    sourcej = self.currentSources.get(s1)
                    dij = self.util.calculateDistanceBetweenDestinations(sourcei, sourcej)
                    if dij < mincij:
                        mincij = dij
        dunnMax = mincij/dk
        return dunnMax


    ## Davies Bouldin Index
    def measureQualityDaviesBouldin(self):
        totalDB = 0
        #print("Number of sources = " + str(len(self.currentSources)))
        for i in self.currentSources:
            source = self.currentSources.get(i)
            maxDbi = 0
            sigmai = 0
            for d in source.destinations:
                sigmai += self.util.calculateDistanceBetweenDestinations(d, source)
            sigmai = sigmai/len(source.destinations)
            for j in self.currentSources:
                if i!=j:
                    source2 = self.currentSources.get(j)
                    sigmaj = 0
                    for d in source2.destinations:
                        sigmaj+=self.util.calculateDistanceBetweenDestinations(d,source2)
                    sigmaj = sigmaj/len(source2.destinations)
                    dij= self.util.calculateDistanceBetweenDestinations(source2, source)
                    db = (sigmaj+sigmai)/dij
                    if maxDbi < db:
                        maxDbi = db

            totalDB+= maxDbi
        totalDB= totalDB/len(self.currentSources)
        return totalDB


    #def measureQualitySilhoutteCoefficient(self):
        #interClusterAverage = 0
        #intraCl



    def saveResultsToDatabase(self):
        self.sourceDao.createSourceTable()
        self.sourceDao.populateSourceTable(self.minSources)
        self.sourceDao.createCatchmentAreas(self.minSources.get())



    def saveDestToSourceMapping(self, run):
        self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations, run)

    def getNumberOfFacilitiesForThisPart(self, dests):
        totalDemand = 0
        #print("Total demand in region " + str(self.totalDemandInTheRegion))
        for d in dests:
            totalDemand+= d.demand
        proportion = totalDemand/self.totalDemandInTheRegion
        #print("My prop " + str(proportion))
        kProp = int(proportion*params['k'])
        return kProp

    def areDemandPointsRandom(self, dests):
        boundingBox = {}
        list ="("
        for d in dests:
            list+=str(d.id) + ", "
        list = list[:-2]
        list += ")"
        rows = self.destinationDao.getBoundingBox(self.distType,list)
        boundingBox['xmin'] = rows['xmin']
        boundingBox['ymin'] = rows['ymin']
        boundingBox['xmax'] = rows['xmax']
        boundingBox['ymax'] = rows['ymax']
        #print("BB " + str(boundingBox))
        #boundingBox['x_min']= rows[0]['xmin']


        normalityTester = NormalityTester.NormalityTester(dests, self.util, boundingBox, self.destinationDao.getRegion(self.distType,list))

        return normalityTester.checkForNormality()


    def  checkValidityOfParts(self):
        continueDivision = False
        for s in self.parts:
            if not self.parts[s].valid:
                continueDivision = True
                break
        return continueDivision


    def createPartitionsFromSources(self):
        self.parts = {}
        assignedFacilities = 0
        maxDemandPointPart = None
        maxdemandPoints = -1
        '''
        deleteSources = []
        for s in self.currentSources:
            #print("source " + str(s))
            source = self.currentSources.get(s)
            part = Part(source.destinations, s)
            k = self.getNumberOfFacilitiesForThisPart(source.destinations)
            part.k = k
            if part.k <2:
                deleteSources.append(s)
        for s in deleteSources:
            print("deleting s"+ str(s))
            del self.currentSources[s]
        self.doCurrentAssignment()
        '''

        for s in self.currentSources:
            #print("source " + str(s))
            source = self.currentSources.get(s)
            part = Part(source.destinations, s)
            k = self.getNumberOfFacilitiesForThisPart(source.destinations)
            part.k = k

            assignedFacilities+= part.k
            self.parts[s] = part
            if part.totalDemandPoints > maxdemandPoints:
                maxDemandPointPart = part
                maxdemandPoints = part.totalDemandPoints
            #print("n = "+ str(len(part.destinations)))
            #print("p = " + str(part.k))
            part.homogeneous = self.areDemandPointsRandom(source.destinations)
            #print("Is this part homogeneous " + str(part.homogeneous) )
            if len(part.destinations) < int(params['maxN']) or part.k < params['maxP']:
                part.valid = True
            if part.homogeneous:
                part.valid = True


        if assignedFacilities < params['k']:
            remaining = params['k']- assignedFacilities
            maxDemandPointPart.k += remaining
            maxDemandPointPart.valid = False
            maxDemandPointPart.homogeneous = self.areDemandPointsRandom(maxDemandPointPart.destinations)
            if len(maxDemandPointPart.destinations) <= params['maxN'] or maxDemandPointPart.k <= params['maxP']:
                maxDemandPointPart.valid = True
            if maxDemandPointPart.homogeneous:
                maxDemandPointPart.valid = True
            self.parts[maxDemandPointPart.id] = maxDemandPointPart

    def printParts(self):
        print("Total Parts " + str(len(self.parts)))
        for s in self.parts:
            print("************************************")
            part = self.parts.get(s)
            part.printPart()

    def getClosestPart(self, id):
        minDistance = sys.maxsize
        closestSrc = -1
        me = self.currentSources.get(id)
        for s in self.currentSources:
            if s!=id :
                source  = self.currentSources.get(s)

                dis = self.util.calculateDistanceBetweenDestinations(me, source)
                if minDistance > dis:
                    minDistance = dis
                    closestSrc = s
        return closestSrc

    def mergeParts(self):
        reducedParts = {}
        for p in self.parts:
            currentPart = self.parts[p]
            if not currentPart.homogeneous:
                reducedParts[p] = Part(currentPart.destinations, currentPart.id)
                reducedParts[p].k = currentPart.k
                reducedParts[p].homogeneous = currentPart.homogeneous
                reducedParts[p].valid = currentPart.valid

                currentPart.parent= p
        for p in self.parts:
            currentPart = self.parts[p]
            if currentPart.parent==-1 :
                mybuddy= self.getClosestPart(p)
                mybuddyPart  = self.parts.get(mybuddy)
                if mybuddyPart.parent!=-1 :
                    redPart = reducedParts.get(mybuddyPart.parent)
                    for d in currentPart.destinations:
                        redPart.destinations.append(d)
                    redPart.totalDemandPoints += len(currentPart.destinations)
                    redPart.k += currentPart.k
                    currentPart.parent = mybuddy
                else:
                    reducedParts[p] = Part(currentPart.destinations, currentPart.id)
                    reducedParts[p].k = currentPart.k
                    reducedParts[p].homogeneous = currentPart.homogeneous
                    reducedParts[p].valid = currentPart.valid
                    currentPart.parent = p
                    redPart = reducedParts[p]
                    # merge my homeless buddy with me
                    for d in mybuddyPart.destinations:
                        redPart.destinations.append(d)
                    redPart.totalDemandPoints += len(mybuddyPart.destinations)
                    redPart.k += mybuddyPart.k
                    mybuddyPart.parent = p

        print("Length of merged parts " + str(len(reducedParts)))
        print("All ks ")
        allk = 0
        self.parts = reducedParts
        self.currentDestinationToSourceMapping = {}
        for p in self.parts:
            part = self.parts.get(p)
            if part.k ==0:
                print("Gotta merge\n\n")
            allk+= part.k
            for d in part.destinations:
                self.currentDestinationToSourceMapping[d.id] = p

        print(" total k= " + str(allk))
        if allk!=100:
            print("Uh Oh \n\n")
            exit(0)

                # get neighbors and assigned to a heterogeneous part if closest
        # bfs on the rest homogeneous

    def mergePartsByDeletingSources(self):
        deletedSources = []
        for s in self.parts:
            part = self.parts.get(s)
            if part.homogeneous or part.k <2:
                deletedSources.append(s)
        for s in deletedSources:
            del self.currentSources[s]

        self.doCurrentAssignmentActual()
        self.createPartitionsFromSources()





# each decomposition part
class Part:
    def __init__(self, destinations, id):
        self.destinations = destinations
        self.id = id
        self.totalDemandPoints = len(self.destinations)
        self.k = -1
        self.sources = {} # after gria
        self.valid = False #valid if either solvable or random
        self.homogeneous = False
        self.assigned = False
        self.parent = -1

    def printPart(self):
        print("Part "+ str(self.id))
        print("Demand " + str(len(self.destinations)))
        print("Facilities to be located "+ str(self.k))
        print("Is part Homogeneous " + str(self.homogeneous))