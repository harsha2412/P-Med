import PartitioningManager
import logging
import csv
import statistics
import copy
import sys
import timeit
import PMedianGrid
import DestinationCreator
from Algorithms import GRIA, Maranzana, FI, FI_Parallel
from Model import  Source
from Cofig import  params, syntheticParams, runs
from FixedPositionsGrid import UniformPartitioning
class LowCalManager:
    def __init__(self):

        #self.pmedianGrid = PMedianGrid.PMedianGrid(params['size'],params['totalPopulation'])
        #self.dsCreator = DestinationCreator.DestinationCreator(self.pmedianGrid)
		#self.dsCreator.createUniformDestinations()
        #self.dsCreator.createMultiClusterDestinations()
		#self.dsCreator.createMultiClusterDestinations()
        #exit(0)

        #self.distType = 'MultipleClusters'
        self.distType = 'dallas'
        params['k'] = 400
        self.distType = 'losangeles'
        params['k'] = 1600
         
        self.distType = 'region6'
        params['k'] = 512
        self.distType = 'losangeles'
        params['k'] = 1600
        
        self.distType = 'texas'
        params['k'] = 3750
        params['kEnd'] = 3750
        logging.basicConfig(filename="logs/"+self.distType+'_plswrk.log',level=logging.INFO)
        #self.distType = 'Random'
        #k = params['k']

        print("Distribution type = " + str(self.distType) + "k = " + str(params['k']))
        logging.info("Distribution type = " + str(self.distType) + "k = " + str(params['k']))

        #vanilla mip

		#
        # k = params['kStart']
        '''
        k = params['k']
        while (params['k']<=params['kEnd']):
            start = timeit.default_timer()
            pm = PartitioningManager.PartitioningManager(k, self.distType)
            pm.fi = FI_Parallel.FastInterchange(params['k'], self.distType)
            pm.fi.getAllDestinations()
            pm.fi.fastInterchange()
            stop = timeit.default_timer()
            difff = (stop - start)/3600
            logging.info("**********************\n\n cost: " +  str(pm.fi.calculateCurrentCost()) + ", time after plain mip " + str(difff) + " hours  *******************************\n\n" )

        #     k = k*2
		#
        '''
        self.useEMClusters()
        
    def saveCostData(self, fileName, data):
        fileName = "sc2020/"+fileName
        with open(fileName, 'w') as f:
            print('wrting to csv' + str(fileName))
            writer = csv.writer(f)
            writer.writerows(data)
            
            
    def useEMClusters(self):
        finalData = []
        #fileName = "n_" + str(params['blockgroups']) + "_" +  self.distType+"_k_"+str(params['k'])+"_merge_mip_fi"+".csv"
        fileName = self.distType+"_k_"+str(params['k'])+"_merge_mip_fi_nonparallel"+".csv"
        clusterFileName =  "n_" + str(params['blockgroups']) + "_" +  self.distType+"_k_"+str(params['k']) + "_indexes.csv"
        p = 2
        scores  = {}
        ps =[]
        selectedPs = []
        selectedDistancePs = []
        ins = 1
       
        pm = None
        cnt = 5
        clusterIndexes = []
        while cnt<=5:
            start = timeit.default_timer()
            print(" trial "+ str(cnt))
            logging.info(" trial "+ str(cnt))
            while ins<=params['selectionRuns']:
                row = [ins]
                print(ins)
                
                #clusterIndexes.append(i)
                pm = PartitioningManager.PartitioningManager(p, self.distType)
                pm.em.getAllDestinations()
                while p  <= params['maxP'] :
                    pm.em.k = p
                    scores[p] = {}
                    ps.append(p)
                   
                    sc = pm.em.createGmmClusters()
                    scores[p] = sc
                    p+=1
                results = pm.evaluateP(scores)
                selectedPs.append(results['densityEstimates'])
                selectedDistancePs.append(results['clustering'])
                p=2
                ins+=1
            ins = 1
            print(selectedPs)
        
            medianP = int(statistics.median(selectedPs))
            medianPCluster = int(statistics.median(selectedDistancePs))
            medianPCluster = min(medianPCluster, medianP,10)
            medianPCluster_org = medianPCluster 
            print("winner for distance " + str(medianP))
            print("winner " + str(medianP))
            #exit(0)
            j=0
            minCost = sys.maxsize
            minSourceIds = []
    
            minCost = sys.maxsize
            minSources = []
            
            dests = {} 
            pm = PartitioningManager.PartitioningManager(medianP, self.distType)
            pm.em.getAllDestinations()
            dests = copy.deepcopy(pm.em.destinations)
            ltime = 0
            gtime = 0
            gcost = 0
            gtime = 0 
            brakFlag = False
            while(j<params['instances']):
                print("******************** whole instance " + str(j)+ " *********************************************************\n\n")
                logging.info("******************** whole instance " + str(j)+ " *********************************************************\n\n")
                pm = PartitioningManager.PartitioningManager(medianP, self.distType)
                pm.em.getAllDestinations()
                #dests = copy.deepcopy(pm.em.destinations)
                pm.em.createGmmClusters(True)
                pm.em.createParts(True) # Make it true for distance analysis
                medianP = len(pm.em.parts)
                print("Number of em current sources == " + str(len(pm.em.currentSources)))
                if len(pm.em.currentSources) ==0:
                    exit(0)
                    pm.k = medianPCluster
                    pm.em.k = medianPCluster
                    pm.em.createGmmClusters(True) ## plot flag is true
                    pm.em.createParts(False) # Dont merge
                
                #pm.em.sourceDao.savePartBoundaries(pm.em.partToDestinationMap, "nmp_silhouette")
                j+=1
                sourceIds = pm.assignPartsToProcessesForMIP(pm.em.parts)
                pm = PartitioningManager.PartitioningManager(params['k'], self.distType)
                # try multiple instances with this p
                pm.fi = FI_Parallel.FastInterchange(params['k'], self.distType)
                i = 1
                pm.fi.destinations = copy.deepcopy(dests)
                if len(sourceIds) != params['k']:
                    logging.info("Not sure ehst hsppened selected only"+ str(len(sourceIds))+  " sources") 
                    brakFlag = True
                    continue
                for s in sourceIds:
                    dest = pm.fi.destinations.get(s)
                    source = Source.Source(dest.x, dest.y, dest.id, i)
                    pm.fi.currentSources[i] = source
                    i += 1
                #pm.fi
                #pm.fi.doCurrentAssignment(pm.gria.currentSources)
                pm.fi.doInitialAssignment()
                cost = pm.fi.calculateCurrentCost()
                if cost < minCost:
                    minCost = cost
                    minSources = sourceIds
                stop = timeit.default_timer()
                gtime = (stop-start)/3600
                gcost = minCost
                print("time and cost after gmm " + str(gcost) + ", " + str(gtime))
                logging.info("time and cost after gmm " + str(gcost) + ", " + str(gtime))
                print("Cost for this instance " +str(cost))
                logging.info("Cost for this instance " +str(cost))
                print("Divinding by distance into " + str(medianPCluster))
                logging.info("Divinding by distance into " + str(medianPCluster))
                disData = []
                medianPCluster_org = medianPCluster
                prevCost = gcost
                disCost = 0
                while medianPCluster >=1 and disCost!=prevCost :
                    print("*********medianPCluster  = "+ str(medianPCluster) + "\n")
                    logging.info("*********medianPCluster  = "+ str(medianPCluster) + "\n")
                    prevCost = disCost
                    pm.em.k = medianPCluster
                    pm.em.destinations = {}
                    for s,src in pm.fi.currentSources.items():
                        pm.em.currentSources[s] = pm.fi.currentSources[s]
                    pm.em.clusterSources()
                    sourceIds = pm.createAndRunFIInstances()
                    pm = PartitioningManager.PartitioningManager(params['k'], self.distType)
                    # try multiple instances with this p
                    pm.fi = FI_Parallel.FastInterchange(params['k'], self.distType)
                    pm.fi.destinations = copy.deepcopy(dests)
                    i = 1
                    for s in sourceIds:
                        dest = pm.fi.destinations.get(s)
                        source = Source.Source(dest.x, dest.y, dest.id, i)
                        pm.fi.currentSources[i] = source
                        i += 1
                    pm.fi.doInitialAssignment()
                    disCost = pm.fi.calculateCurrentCost()
                    lcost = disCost
                    stop = timeit.default_timer()
                    ltime = (stop-start)/3600
                    disData.append([medianPCluster, disCost,ltime])
                    print("Cost for this instance fpr" + str(medianPCluster) +  "after distance division = " +str(disCost) + "time = " + str(ltime))
                    logging.info("Cost for this instance fpr" + str(medianPCluster) +  "after distance division = " +str(disCost) + "time = " + str(ltime))
                    medianPCluster -=1 
                logging.info("I got here")
                self.saveCostData(self.distType+str(params['k'])+"_trial" +str(cnt)+ "_distanceClusters.csv",disData)

            if brakFlag:
                continue
            if medianPCluster > 1:
                print("time and cost after distance " + str(disCost) + ", " + str(ltime))
                print("Num of srcs " + str(len(minSources)))
                pm.fi.fastInterchange(parallelize = False)
                stop = timeit.default_timer()
                diff = stop - start
                print("final time = " + str(diff / 3600) + " hours")
                tame = diff/3600
                cost = pm.fi.calculateCurrentCost()
                print("final cost after FI " + str(cost))
                name = "merge_fi_mip" # or
            else:
                tame = ltime
                cost = disCost
            logging.info("appending data")
            #name = "noMerge_Distance"
            #pm.fi.saveDestToSourceMapping(cnt, name)
            #3 "Number of parts, final cost, final time, time after gmm, cost after gmm"
            finalData.append([medianP,medianPCluster_org, cost, tame, ltime, lcost, gtime, gcost])
            #finalData.append([medianP, cost, tame,ltame,lcost, pm.gria.localSwapCount, pm.gria.globalSwapCount, pm.gria.iterations  ])
            cnt+=1

        #path = "sc2020/"
        self.saveCostData(fileName,finalData)


    def saveTimes(self, fileName, times):
        data = []
        for k in times:
            data.append([k, times.get(k)])
        with open(fileName, 'w') as f:
            # print('wrting to csv')
            writer = csv.writer(f)
            writer.writerows(data)

    def getPartsBasedOnValidity(self):
        p = 2
        pm = None
        validityCondition = False
        start = timeit.default_timer()
        while not validityCondition:
            print("****************************************************************************************************\n\n")
            print("p = "+ str(p))
            pm = PartitioningManager.PartitioningManager(p, self.distType)
            pm.k = p
            pm.runMaranzanaForDecomposition()
            pm.maranzana.createPartitionsFromSources()
            validityCondition = not pm.maranzana.checkValidityOfParts()
            p = p+1

        p=p-1
        print("p selected for decomposition " + str(p))

        maranzanaRuns = runs
        mrz =0
        minCost = sys.maxsize
        minSourceIds = []
        while mrz<maranzanaRuns:
            print("########################## mrz Run " + str(mrz) + "##################################################")
            pm = PartitioningManager.PartitioningManager(p, self.distType)
            pm.k = p
            validityCondition = False
            validCounter = 0
            while not validityCondition:
                print("p = " + str(p) + "validity counter " + str(validCounter))
                pm = PartitioningManager.PartitioningManager(p, self.distType)
                pm.k = p
                pm.runMaranzanaAfterPIsKnown()
                pm.maranzana.createPartitionsFromSources()
                validityCondition = not pm.maranzana.checkValidityOfParts()
                validCounter +=1
            #pm.maranzana.mergeParts()
            pm.maranzana.mergePartsByDeletingSources()
            #pm.maranzana.sourceDao.saveParts(pm.maranzana.currentDestinationToSourceMapping,pm.maranzana.destinations, len(pm.maranzana.parts))
            #exit(0)
            sourceIds = []
            for par in pm.maranzana.parts:
                print("part " + str(par))
                part = pm.maranzana.parts.get(par)
                pm.gria = GRIA.GRIA(part.k, self.distType)
                print(" My k " + str(part.k))
                print(" My destinations " + str(len(part.destinations)))
                for d in part.destinations:
                    pm.gria.destinations[d.id] = d
                pm.runGria()
                for s in pm.gria.minSources:
                    src = pm.gria.minSources.get(s)
                    sourceIds.append(src.destinationId)
            pm.maranzana = Maranzana.Maranzana(params['k'], self.distType)
            pm.maranzana.getAllDestinations()
            pm.maranzana.buildDistanceMap()
            i = 1
            print("Length of sourceids " + str(len(sourceIds)))

            for s in sourceIds:
                dest = pm.maranzana.destinations.get(s)
                source = Source.Source(dest.x, dest.y, dest.id, i)
                pm.maranzana.currentSources[i] = source
                i += 1
            pm.maranzana.doCurrentAssignment()
            prevCost = pm.maranzana.calculateCurrentCost()
            print("final cost before global maranzana " + str(prevCost))
            pm.runMaranzana()
            pm.maranzana.doCurrentAssignment()
            afterCost = pm.maranzana.calculateCurrentCost()
            print("cost after global maranzana " + str(afterCost))
            if afterCost < prevCost:
                print("Global Maranzana helped")
                sourceIds = []
                for s in pm.maranzana.currentSources:
                    src = pm.maranzana.minSources.get(s)
                    sourceIds.append(src.destinationId)
            cost = prevCost
            if afterCost < prevCost:
                cost = afterCost

            if minCost > cost:
                minCost = cost
                minSourceIds = {}
                minSourceIds = sourceIds.copy()

            mrz+=1


        print("Final solution cost " + str(minCost) + " Number of sources "+ str(len(minSourceIds)))
        i = 1
        sourceIds = []
        for s in minSourceIds:
            #dest = pm.maranzana.destinations.get(s)
            #source = Source.Source(dest.x, dest.y, dest.id, i)
            sourceIds.append(s)


        ## post gria
        pm.gria  = GRIA.GRIA(params['k'], self.distType)
        pm.gria.getAllDestinations()
        pm.gria.buildDistanceMap()
        i = 1

        for s in sourceIds:
            dest = pm.gria.destinations.get(s)
            source = Source.Source(dest.x, dest.y, dest.id, i)
            pm.gria.currentSources[i] = source
            i+=1
        pm.gria.doCurrentAssignment(pm.gria.currentSources)
        cost = pm.gria.calculateCurrentCost()
        print("final cost before gria " + str(cost))
        stop = timeit.default_timer()
        diff = stop - start
        print("time before gria local = " + str(diff / 3600) + " hours")
        pm.runGriaGlobalOnly()
        pm.gria.doCurrentAssignment(pm.gria.currentSources)
        stop = timeit.default_timer()
        diff = stop - start
        print("time = " + str(diff/3600) + " hours")
        cost = pm.gria.calculateCurrentCost()
        print("final cost after local gria  " + str(cost))
        pm.gria.saveDestToSourceMapping()





        stop = timeit.default_timer()
        diff = stop - start
        print("time = " + str(diff / 3600) + " hours")


        ## RUN Marnazana now

        #pm.maranzana.saveDestToSourceMapping("final_maranzana_end_decomposed_" + str(params["trial"]))


class gridManager:
    def __init__(self, size, pods):
        self.up = UniformPartitioning.UniformPartitioning(size, pods)
        #self.up.mapBlockGroupsToPodsByDistance()
        self.up.mapBlockGroupsToPods()
        self.up.createCatchmentAreas()
        self.up.calculateTotalCost()
        print('total Cost !!! = ')
        print(self.up.totalCost)
        #self.up.printBlockGroupMembership()
        self.up.regionCreator.plotRegion()

        self.up.regionCreator.plotInitialPartitions()
        self.up.getHomies()
        #self.up.regionCreator.plotPartition3ForTesting()
        #self.up.balancePartitions()
        #self.up.printBlockGroupMembership()
        #self.up.regionCreator.plotPartitions()

        self.up.totalCost = 0
        self.up.calculateTotalCost()
        print('total Cost !!! = ')
        print(self.up.totalCost)

        #self.up.regionCreator.plotPartition3ForTesting()
        self.up.regionCreator.plotPartitions()




#lowCalManager = LowCalManager()
#gridMan = gridManager(10,5)
#gridMan = gridManager(30,10)
#gridMan = gridManager(5,5)

lowCalManager = LowCalManager()

## k = 4 to 128
# size = 100
## N = 500,000
## number of destinations = 350
