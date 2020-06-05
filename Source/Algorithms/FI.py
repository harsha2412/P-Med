import sys
import collections
import random

from DAOs import SourceDAO
from DAOs import DestinationDAO
from Model import Source
from Model import Destination
import Utilities as util
class FastInterchange:
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
                self.destIdToSourceId = {}
                self.closestSources = {} # did to did
                self.secondClosestSource = {} # did t o did

        def getAllDestinations(self):
                #results = self.destinationDao.getAllSyntheticDestinations(self.distType)
                results = self.destinationDao.getAllDestinations()
                for row in results:
                        newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
                        self.destinations[newDestination.id] = newDestination
                self.n = len(self.destinations)
                
                
        ## implemented from VNS + FI paper
        def moveEval(self, goin):
                w=0
                change = {} # destId for source being deleted to change
                for s in self.currentSources:
                        change[self.currentSources.get(s).destinationId]  = 0
                for d in self.destinations:
                        if self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin)) < self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.secondClosestSource[d])):
                                w = w+ self.destinations.get(d).demand* (self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin)) - self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.closestSources[d])))
                                #change[self.closestSources[d]] = change[self.closestSources[d]] + self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin)) - self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.closestSources[d]))
                                #w=w
                        else:
                                change[self.closestSources[d]] = change[self.closestSources[d]] +  self.destinations.get(d).demand*(min(self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin)), self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.secondClosestSource[d]))) - self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.closestSources[d])))
                g = sys.maxsize
                goOut = -1
                
                for s_did in change:
                        if change[s_did] < g:
                                g = change[s_did]
                                goOut = s_did
                w = w+g
                move= {}
                move['goOut'] = goOut
                move['w'] = w
                #print("Move eval " +  str(move))
                return move
        
        def myMoveEval2(self, goin_min):
                backUpClosest = {}
                for d in self.closestSources:
                        backUpClosest[d] = self.closestSources[d]
                changeCausedByRemoving = {}  # source's destid to cost
                currentCost = self.calculateCostUpdated()
                #backUpSecondClosest =
                for s in self.currentSources:
                        gout_min = self.currentSources.get(s).destinationId
                        for d in self.destinations:
                                if self.closestSources[d] == gout_min:
                                        if self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin_min)) < self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.secondClosestSource[d])):
                                                self.closestSources[d] = goin_min
                                                #print("1. I am changing the source for dest " + str(d) + " from " + str(gout_min) + " to " + str(goin_min))
                                                #print("Prev cost")
                                                #self.calculateCurrentCost()
                                                #print("after cost")
                                                #self.calculateCurrentCost()
                                        else:
                                                self.closestSources[d] = self.secondClosestSource[d]
                                                #print("2. I am changing the source for dest " + str(d) + " from " + str(gout_min) + " to " + str(self.secondClosestSource[d]))
                                else:
                                        if self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.closestSources[d]) ) > self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin_min)):
                                                #print("3. I am changing the source for dest " + str(d) + " from " + str(gout_min) + " to " + str(goin_min))
                                                self.closestSources[d] = goin_min
                        changeCausedByRemoving[gout_min] =  self.calculateCostUpdated() - currentCost
                        for d in backUpClosest:
                                self.closestSources[d] = backUpClosest[d]
                w = sys.maxsize
                goOut = -1
                for sdid in changeCausedByRemoving:
                        if changeCausedByRemoving.get(sdid) < w:
                                w = changeCausedByRemoving.get(sdid)
                                goOut = sdid
                move = {}
                move['goOut'] = goOut
                move['w'] = w
                #print("For goin " + str(goin_min) + " best move = " + str(move))
                return move
                
        def costDiffByAdding(self, goin, prevCost):
                goOut = -1
                minCost = sys.maxsize
                closestSourceBackUp  = {}
                for d in self.destinations:
                        closestSourceBackUp[d] = self.closestSources[d]
                for s in self.currentSources:
                        costOfThisExchange = 0
                        currentSource= self.currentSources.get(s)
                        currentSourceDestId = currentSource.destinationId
                        for d in self.destinations:
                                dest = self.destinations.get(d)
                                if self.closestSources.get(d) == currentSourceDestId:
                                        if self.util.calculateDistanceBetweenDestinations(dest, self.destinations.get(self.secondClosestSource.get(d))) <= self.util.calculateDistanceBetweenDestinations(dest, self.destinations.get(goin)):
                                                self.closestSources[d] = self.secondClosestSource.get(d)
                                        else:
                                                self.closestSources[d] = goin
                                elif self.util.calculateDistanceBetweenDestinations(dest, self.destinations.get(self.closestSources.get(d))) > self.util.calculateDistanceBetweenDestinations(dest, self.destinations.get(goin)):
                                        self.closestSources[d] = goin
                        costOfThisExchange = self.calculateCostUpdated()
                        if minCost > costOfThisExchange:
                                goOut = currentSourceDestId
                                minCost = costOfThisExchange
                        self.closestSources = {}
                        for d in self.destinations:
                                self.closestSources[d] = closestSourceBackUp[d]
                diff = minCost - prevCost
                move = {}
                move['goOut'] = goOut
                move['w'] = diff
                # print("For goin " + str(goin_min) + " best move = " + str(move))
                return move

                
                        
                                                
        def myMoveEval(self, goin):
                goOut = -1
                changeCausedByRemoving = {} #source's destid to cost
                #netChangeIn
                w = sys.maxsize
                fixedCost = 0
                for s in self.currentSources:
                        #print("Current Sources " + str(self.currentSources.get(s).destinationId))
                        changeCausedByRemoving[self.currentSources.get(s).destinationId] = 0
                        
                for d in self.destinations:
                        #print(" I am destination " + str(d))
                        
                        mySource = self.closestSources[d]
                        currentDistance = self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(mySource))
                        #print("  I am currently assigned to " + str(mySource))
                        # assume mySource is Deleted
                        #print("  I am currently assigned to " + str(mySource) + ", My current distance is  " + str(currentDistance))
                        newDistance = self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin))
                        if newDistance < currentDistance:
                                fixedCost+=  self.destinations.get(d).demand*(newDistance - currentDistance)
                        else:
                                c2Distance = self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.secondClosestSource[d]))
                                if newDistance > c2Distance:
                                        newDistance = c2Distance
                                
                                #print("My new distance is " + str(newDistance))
                                changeCausedByRemoving[mySource] =      changeCausedByRemoving[mySource] + self.destinations.get(d).demand*(newDistance-currentDistance)
                        
                for sdid in changeCausedByRemoving:
                        #
                        #print(" Removal of " + str(sdid ) + " leads " + str(changeCausedByRemoving.get(sdid)) + " cost change")
                        
                        if changeCausedByRemoving[sdid] < w:
                                w = changeCausedByRemoving[sdid]
                                goOut = sdid
                move = {}
                move['goOut'] = goOut
                move['w'] = w+fixedCost
                #print("\n\n*********************************************\n")
                #print("Move eval " + str(goin)  + ": " + str(move))
                return move
 
        
        
        def updateClosestAndSecondClostest(self, goin_min, gout_min):
                #print("DO I ocme heerrre\n\n")
                for d in self.destinations:
                        if self.closestSources[d] == gout_min:
                                if self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin_min)) < self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.secondClosestSource[d])):
                                        self.closestSources[d] = goin_min
                                        #print("1. I am changing the source for dest " + str(d) + " from " + str(gout_min) + " to " + str(goin_min))
                                        #print("Prev cost")
                                        #self.calculateCurrentCost()
                                        self.currentDestinationToSourceMapping[d] = goin_min
                                        #print("after cost")
                                        #self.calculateCurrentCost()
                                else:
                                        self.closestSources[d] = self.secondClosestSource[d]
                                        #print("2. I am changing the source for dest " + str(d) + " from " + str(gout_min) + " to " + str(self.secondClosestSource[d]))
                                        self.currentDestinationToSourceMapping[d] = self.secondClosestSource[d]
                                        self.secondClosestSource[d] = self.pickSecondMinSource(d)
                        else:
                                if self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.closestSources[d]) ) > self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin_min)):
                                        #print("3. I am changing the source for dest " + str(d) + " from " + str(gout_min) + " to " + str(goin_min))
                                        self.secondClosestSource[d] = self.closestSources[d]
                                        self.closestSources[d] = goin_min
                                        self.currentDestinationToSourceMapping[d] = goin_min
                                elif self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(goin_min)) < self.util.calculateDistanceBetweenDestinations(self.destinations.get(d), self.destinations.get(self.secondClosestSource[d])):
                                                self.secondClosestSource[d] = goin_min
                                elif self.secondClosestSource[d] == gout_min:
                                        self.secondClosestSource[d] = self.pickSecondMinSource(d)
                for d in self.closestSources:
                        if self.closestSources.get(d) == gout_min:
                                print("Uh oh ")
                                exit(0)
                                        
                
                
        def fastInterchange(self):
                self.iterations = 0
                if len(self.currentSources) ==0:
                        print("random sources in fi")
                        currentKeys = random.sample(list(self.destinations), self.k)
                        i = 1
                        self.currentSources = {}
                        for k in currentKeys:
                                dest = self.destinations.get(k)
                                self.tabooList[k] = dest
                                source = Source.Source(dest.x, dest.y, dest.id, i)
                                i += 1
                                self.currentSources[source.id] = source
                currentKeys = []
                for s in self.currentSources:
                        currentKeys.append(self.currentSources[s].destinationId)

                self.doInitialAssignment() ## optimized step in the
                self.initializeSecondClosestSource()
                fopt = self.calculateCostUpdated()
                print("Initial cost " + str(fopt))
                terminationCondition = False
                complementKeys = []
                for d in self.destinations:
                        if d not in currentKeys:
                                complementKeys.append(d)
                while not terminationCondition:
                        fopt = self.calculateCostUpdated()
                        print("\n~~~~~~~~~~~~~~Iteration: " + str(self.iterations))
                        wmin = sys.maxsize
                        goin_min = -1
                        gout_min = -1
                        for goin in complementKeys:
                                res = self.myMoveEval(goin)
                                if wmin > res['w']:
                                        wmin = res['w']
                                        #print("I found a reduced wmin" + str(wmin))
                                        goin_min = goin
                                        gout_min = res['goOut']
                        #print("################################\n wmin = " + str(wmin))
                        self.iterations+=1
                        if wmin >=0:
                                print("Extermination!!")
                                #self.doCurrentAssignment()
                                fCost = self.calculateCostUpdated()
                                print("final cost = " + str(fCost))
                                #exit(0)
                                
                                
                                
                                terminationCondition = True
                                
                        else:
                                fopt = fopt + wmin
                                #print("\n swap change " +  str(gout_min) + " to " + str(goin_min) + "\n")
                                sourceIdToUpdate = self.destIdToSourceId[gout_min]
                                #print("Updating source id " + str(sourceIdToUpdate) + " to " + str(goin_min))
                                self.currentSources[sourceIdToUpdate] = Source.Source(self.destinations.get(goin_min).x, self.destinations.get(goin_min).y, goin_min, sourceIdToUpdate )
                                self.updateClosestAndSecondClostest(goin_min, gout_min)
                                #self.doCurrentAssignment()
                                print("New fopt " + str(fopt))
                                
                                self.calculateCostUpdated()
                                self.destIdToSourceId = {}
                                for s in self.currentSources:
                                        source = self.currentSources.get(s)
                                        self.destIdToSourceId[source.destinationId] = s
                                ind =0
                                for key in complementKeys:
                                        if key == goin_min:
                                                complementKeys[ind] = gout_min
                                                break
                                        ind+=1
        
        def saveDestToSourceMapping(self, cnt, name):
                #self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations, cnt, name)
                self.sourceDao.saveSourcesReal(self.currentDestinationToSourceMapping, self.destinations)
        
        #def saveDestToSourceMapping(self):
                #self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations)
        
             #self.sourceDao.saveSourcesReal(self.currentDestinationToSourceMapping, self.destinations)
        
        def initializeCurrentSources(self, sources):
                self.currentSources = dict(sources)
        
        # self.current_r_value = self.calculateCurrentCost()
                
                
        
        def pickMinSource(self, destination):
                min = sys.maxsize
                minSource = 1
                minsid = -1
                for source in self.currentSources:
                        #sid = self.currentSources[source].id
                        # print("hererre "+ str(sid))
                        s = self.currentSources[source].destinationId
                        if self.util.calculateDistanceBetweenDestinations(self.destinations[s], self.destinations[destination]) < min:
                                min = self.util.calculateDistanceBetweenDestinations(self.destinations[s], self.destinations[destination])
                                minSource = s
                                minsid = source
                sourceToUpdate = self.currentSources.get(minsid)
                if self.currentSources.get(minsid) is None: 
                    print("sid = " + str(minsid))
                    print(str(list(self.currentSources.keys())))
                self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
                return minSource
        
        def pickSecondMinSource(self, destination):
                min = sys.maxsize
                minSource = 1
                minsid = -1
                for source in self.currentSources:
                        sid = self.currentSources[source].id
                        # print("hererre "+ str(sid))
                        s = self.currentSources[source].destinationId
                        if self.util.calculateDistanceBetweenDestinations(self.currentSources[source],self.destinations[destination]) < min and s!=self.closestSources[destination]:
                                min = self.util.calculateDistanceBetweenDestinations(self.currentSources[source], self.destinations[destination])
                                minSource = s
                                minsid = sid
                # print("closest source "+ str(minsid))
                self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
                return minSource
        
        def doInitialAssignment(self):
                for s in self.currentSources:
                        self.currentSources.get(s).destinations = []
                for d in self.destinations:
                        self.currentDestinationToSourceMapping[d] = self.pickMinSource(d)
                        self.closestSources[d] = self.currentDestinationToSourceMapping[d]
                self.destIdToSourceId = {}
                for s in self.currentSources:
                        source = self.currentSources.get(s)
                        self.destIdToSourceId[source.destinationId] = s
                        
        def doCurrentAssignment(self):
                for s in self.currentSources:
                        self.currentSources.get(s).destinations = []
                for d in self.destinations:
                        self.currentDestinationToSourceMapping[d] = self.pickMinSource(d)
                self.destIdToSourceId = {}
                for s in self.currentSources:
                        source = self.currentSources.get(s)
                        self.destIdToSourceId[source.destinationId] = s
                        
        def initializeSecondClosestSource(self):
                for d in self.destinations:
                        self.secondClosestSource[d] = self.pickSecondMinSource(d)
        
        def calculateCurrentCost(self):
                cost = 0.0
                for d in self.currentDestinationToSourceMapping:
                        s = self.currentDestinationToSourceMapping[d]
                        cost += self.util.calculateDistanceBetweenDestinations(self.destinations.get(s),self.destinations.get(d)) * self.destinations.get(d).demand
                #print("\n\nCost = "+ str(cost))
                return cost
        
        def calculateCostUpdated(self):
                cost = 0.0
                for d in self.closestSources:
                        s = self.closestSources[d]
                        cost += self.util.calculateDistanceBetweenDestinations(self.destinations.get(s),self.destinations.get(d)) * self.destinations.get(d).demand
                #print("\n\nCost = " + str(cost))
                return cost
