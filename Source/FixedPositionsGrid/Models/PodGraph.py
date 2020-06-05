import sys
import random
import operator
class PodGraph:
    def __init__(self, podDictionary):
        self.podGraph = {}
        self.pods = podDictionary
        self.sourceSinkPaths = []


    def initializeGraph(self):
        #print('GGGRRRAAAPPPH')
        for pid in self.pods:
            self.podGraph[pid] = {}
            #print('source ' + str(pid))
            p1 = self.pods.get(pid)
            #print(set(p1.polygon.boundary.coords))
            for opid in self.pods:
                #print('dest ' + str(opid))
                if pid !=opid:
                    p1 = self.pods.get(pid)
                    p2 = self.pods.get(opid)

                    if p1.polygon.touches(p2.polygon):
                    #if len(set(p1.polygon.boundary.coords).intersection(p2.polygon.boundary.coords))>=1:
                        self.podGraph[pid][opid] = p1.coordinates.distance(p2.coordinates)
                        #print('dest ' + str(opid)+ ' Edge FOUNDDD')
                        #print('No toucccch')



    def printGraph(self):
        for pid in self.pods:
            for opid in self.pods:
                if self.podGraph.get(pid).get(opid) is not None:
                    print(pid + "--> " + opid + ', distance = ' + str(self.podGraph.get(pid).get(opid)))




    def dfs_for_current_path(self, currentNode, sink, vistedDict, dfsPath, source):
        vistedDict[currentNode] = True
        dfsPath.path.insert(dfsPath.currentValidIndex, currentNode)
        dfsPath.currentValidIndex +=1
        if currentNode == sink:
            ssPath = SourceSinkPath()
            ssPath.sink = sink
            ssPath.source = source
            ssPath.path = []
            for i in range(dfsPath.currentValidIndex):
                ssPath.path.append(dfsPath.path[i])
            ssPath.path.pop(0)
            self.sourceSinkPaths.append(ssPath)

        else:
            for node in self.podGraph.get(currentNode):
                if not vistedDict.get(node):
                    self.dfs_for_current_path(node, sink, vistedDict, dfsPath, source )
        dfsPath.currentValidIndex -= 1
        vistedDict[currentNode] = False

    def dfs(self, source, sink):
        visitedDict = {}
        for k in self.pods:
            visitedDict[k] = False
        dfsPath = DFSTraversalPath()
        self.dfs_for_current_path(source, sink, visitedDict, dfsPath, source)


    def evaluateSourceSinkPaths(self):
        minCostPath = sys.maxsize
        #ind = random.randint(0,len(self.sourceSinkPaths)-1)
        #minPath = self.sourceSinkPaths[ind]
        minCostPath = sys.maxsize
        minPath = self.sourceSinkPaths[0]
        for eachPath in self.sourceSinkPaths:
            # print(eachPath.path)
            eachPath.cost = 0
            currentS = eachPath.source
            for node in eachPath.path:
                sourcePod = self.pods.get(currentS)
                destPod = self.pods.get(node)
                minValWrtBisector = sys.maxsize
                bgToSteal = -1
                for bid in destPod.myHomies:
                    bg = destPod.myHomies.get(bid)
                    line = sourcePod.bisectors[node]
                    lineVal = abs(sourcePod.getSignForThisPoinWithRespectToThisLine(bg.point, line))
                    if minValWrtBisector > lineVal:
                        bgToSteal = bid
                        minValWrtBisector = lineVal

                # print('stealing ' + str(bgToSteal))
                replacingBG = destPod.myHomies.get(bgToSteal)
                eachPath.cost += self.calculateCost(replacingBG.point, destPod.coordinates, sourcePod.coordinates)
                currentS = node

            # print('this path coost '+ str(eachPath.cost))
            if minCostPath > eachPath.cost:
                minCostPath = eachPath.cost
                minPath = eachPath
            # print(minPath.path)
            #print(minPath.path)

        return minPath


    def exchangeOneBgAlongTheMinPath(self, minPath):
        print('Lets look at the min path')
        print(minPath.path)
        currentS = minPath.source
        for node in minPath.path:
            sourcePod = self.pods.get(currentS)
            destPod = self.pods.get(node)
            minValWrtBisector = sys.maxsize
            minValDict = {}
            bgToSteal = -1
            for bid in destPod.myHomies:
                bg = destPod.myHomies.get(bid)
                line = sourcePod.bisectors[node]
                lineVal = abs(sourcePod.getSignForThisPoinWithRespectToThisLine(bg.point, line))
                minValDict[bid] = lineVal
                if minValWrtBisector > lineVal:
                    bgToSteal = bid
                    minValWrtBisector = lineVal

            sorted_bgs = sorted(minValDict.items(), key=operator.itemgetter(1))

            replacingBG = destPod.myHomies.get(bgToSteal)



            #sourcePod.createPolygon()
            count = 1
            ownercondition = False
            if destPod.owner == bgToSteal:
                ownercondition = True

            #while not (replacingBG.boundary.touches(sourcePod.polygon)):

            while ( not (replacingBG.boundary.touches(sourcePod.polygon)) or ownercondition):
                print('doesnt touch!!')
                replacingBG  = destPod.myHomies.get(sorted_bgs[count][0])
                count +=1
                ownercondition = destPod.owner == replacingBG.id
                if count == len(sorted_bgs):
                    print('Nothing touches')
                    replacingBG = destPod.myHomies.get(bgToSteal)
                    break

            print('owner = ' + str(destPod.owner))
            print('donating = ' + str(replacingBG.id))

            del destPod.myHomies[replacingBG.id]
            replacingBG.membership = currentS
            sourcePod.myHomies[replacingBG.id] = replacingBG
            destPod.balance -= 1
            sourcePod.balance += 1
            currentS = node

        ## fix Polygons
        #for node in minPath.path:
           # pod = self.pods.get(node)
            #print('REcreation of polygons for pod' + str(node) + '#homies ' + str(len(pod.myHomies)))
            #pod.createPolygon()






    def calculateCost(self, bgPoint, previousPodPoint, newPodPoint):
        return bgPoint.distance(newPodPoint) - bgPoint.distance(previousPodPoint)



    def makeOneMovement(self):
        mp = self.evaluateSourceSinkPaths()
        self.exchangeOneBgAlongTheMinPath(mp)

class DFSTraversalPath:
    def __init__(self):
        self.path = []
        self.currentValidIndex = 0


class SourceSinkPath:
    def __int__(self, source, sink):
        self.source = source
        self.sink = sink
        self.path = []
        self.cost = 0