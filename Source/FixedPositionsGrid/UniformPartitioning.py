from FixedPositionsGrid import RegionCreator
from FixedPositionsGrid.Models import PodGraph
import sys
class UniformPartitioning:
    def __init__(self, size, pods):
        self.regionCreator = RegionCreator.RegionCreator(size, pods)

        self.region = self.regionCreator.region
        self.getInitialBisectors()
        self.sinks = [] # surplus
        self.sources = [] # deficit
        self.graph = {}
        self.graphUtil = None
        self.totalCost = 0


        #self.regionCreator.plotRegion()



    def getInitialBisectors(self):
        for pid in self.regionCreator.pods:
            for opid in self.regionCreator.pods:
                if pid != opid:
                    p = self.regionCreator.pods.get(pid)
                    op = self.regionCreator.pods.get(opid)
                    p.calculatePerpendicular(op,1,1)
                    p.storeSignsWithRespectToBisector(op)


    def mapBlockGroupsToPods(self):
        for pid in self.regionCreator.pods:
            p = self.regionCreator.pods.get(pid)
            p.myHomies.clear()
        for bid in self.regionCreator.region:
            b = self.regionCreator.region.get(bid)
            for pid in self.regionCreator.pods:
                p = self.regionCreator.pods.get(pid)
                iBelongToThisPod = True
                for otherpods in p.bisectors:
                    line = p.bisectors.get(otherpods)
                    pointSign = p.getSignForThisPoinWithRespectToThisLine(b.point, line)
                    podSign = line['sign']
                    if pointSign*podSign < 0:
                        iBelongToThisPod = False
                        break
                if iBelongToThisPod:
                    b.membership = p.id
                    p.myHomies[b.id] = b
                    break


    def mapBlockGroupsToPodsByDistance(self):
        for bid, bg in self.regionCreator.region.items():
            minDistance = sys.maxsize
            minPod = -1
            for p, pod in self.regionCreator.pods.items():
                dis = pod.coordinates.distance(bg.point)
                if minDistance > dis:
                    minDistance = dis
                    minPod = p
            bg.membership  = minPod
            podHomie = self.regionCreator.pods.get(minPod)
            podHomie.myHomies[bid] = bg




    def printBlockGroupMembership(self):
        for bid in self.regionCreator.region:
            b = self.regionCreator.region.get(bid)
            print(str(b.id) + '--> ' + str(b.membership))




    def sourceSinkSetup(self):
        totalBlocks = len(self.regionCreator.region)
        goalSize = totalBlocks / self.regionCreator.k  ## for the simple scenario
        self.sinks = []
        self.sources = []
        for pid in self.regionCreator.pods:
            p = self.regionCreator.pods.get(pid)
            p.balance = len(p.myHomies) - goalSize
            if p.balance > 0:
                self.sinks.append(pid)
            elif p.balance < 0:
                self.sources.append(pid)

        print('POD Balance Staus ')
        self.printPodBalanceStatus()
        self.graphUtil = PodGraph.PodGraph(self.regionCreator.pods)
        self.graphUtil.initializeGraph()
        #print('Graph')
        #self.graphUtil.printGraph()
        #print('Sinks')
        #print(self.sinks)
        #print('Source')
        #print(self.sources)


    def balancePartitions(self):
        maxIterations = 19
        i = 0
        self.sourceSinkSetup()
        #while (not self.balanceAchieved() and i< maxIterations):
        while (not self.balanceAchieved()):
            #self.graphUtil = PodGraph.PodGraph(self.regionCreator.pods)
            self.getSourceSinkPaths()
            self.graph = self.graphUtil.podGraph
            self.graphUtil.makeOneMovement()
            #self.rePopulateHomies()
            self.createCatchmentAreas()
            self.sourceSinkSetup()
            i+=1
            print('Iteration')
            print(i)

        # self.rebalanceShenaighans()
        #



        #if

    def balanceAchieved(self):
        balanceAchieved = True
        for p in self.regionCreator.pods:
            pod = self.regionCreator.pods.get(p)
            if pod.balance !=0:
                balanceAchieved = False
                break
        return balanceAchieved


    def rebalanceShenaighans(self):
        currentStatus = dict(self.regionCreator.region)
        rebalanceCount = 1
        self.mapBlockGroupsToPods()
        self.rebalanceAll()

        while (not self.checkForChange(currentStatus, self.regionCreator.region)):
            rebalanceCount += 1
            currentStatus = dict(self.regionCreator.region)
            self.rebalanceAll()
            self.up.mapBlockGroupsToPods()
            self.up.createCatchmentAreas()
            self.graphUtil.initializeGraph()
            self.graph = self.graphUtil.podGraph
        print('Rebalance Count')
        print(rebalanceCount)
        self.graph.printGraph()

    def checkForChange(self, dict1, dict2):
        nochange = True
        for k,v in dict1.items():
            if v.membership!=dict2.get(k).membership:
                nochange = False
                break
        return nochange


    def rePopulateHomies(self):
        for pid in self.regionCreator.pods:
            pod = self.regionCreator.pods.get(pid)
            pod.myHomies = {}
        for bid in self.regionCreator.region:
            bg = self.regionCreator.region.get(bid)
            pid = bg.membership
            pod = self.regionCreator.pods.get(pid)
            pod.myHomies[bid] = bg
    def createCatchmentAreas(self):
        for pid in  self.regionCreator.pods:
            pod = self.regionCreator.pods.get(pid)
            pod.createPolygon()

    def rebalancePerpendicluars(self):
        for pid in self.regionCreator.pods:
            p1 = self.regionCreator.pods.get(pid)
            if p1.balance !=0:
                neighbors = self.graph.get(pid)
            for x in neighbors:
                p2 = self.regionCreator.pods.get(x)
                if p2.balance !=0:
                    p1.calculatePerpendicular(p2, len(p2.myHomies), len(p1.myHomies))
                    p1.storeSignsWithRespectToBisector(p2)




    def rebalanceAll(self):
        for pid in self.regionCreator.pods:
            for opid in self.regionCreator.pods:
                if pid != opid:
                    p = self.regionCreator.pods.get(pid)
                    op = self.regionCreator.pods.get(opid)
                    p.calculatePerpendicular(op, len(op.myHomies), len(p.myHomies))
                    p.storeSignsWithRespectToBisector(op)



    def getSourceSinkPaths(self):
        for source in self.sources:
            for sink in self.sinks:
                #print('source ' + str(source))
                #print('sink ' + str(sink))
                self.graphUtil.dfs(source,sink)
        #print(str(len(self.graphUtil.sourceSinkPaths)))
        #for p in self.graphUtil.sourceSinkPaths:
            #print(p.path)



    def printPodBalanceStatus(self):
        for p in self.regionCreator.pods:
            pod = self.regionCreator.pods.get(p)
            #pod.printHomies()
            #print("I am pod " + str(p))
            print( str(p)+ " ---> " + str(pod.balance))
            #print(str(len(pod.myHomies)))


    def calculateTotalCost(self):
        for bid,bg in self.regionCreator.region.items():
            pd = self.regionCreator.pods.get(bg.membership)
            self.totalCost += bg.point.distance(pd.coordinates)



    def getHomies(self):
        facilityIds = []
        facilityCount = []
        for p in self.regionCreator.pods:
            pod = self.regionCreator.pods.get(p)
            facilityIds.append(p)
            facilityCount.append(len(pod.myHomies))


        print(facilityCount)






