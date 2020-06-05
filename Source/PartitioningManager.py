import sys

import csv
from Algorithms import  Maranzana
from Algorithms import TeitzBart
from Algorithms import Myopic
from Algorithms import GRIA, EM, MIP, FI
from Cofig import runs, griaRuns, maranzanaValidityRuns
from Cofig import syntheticParams
from Cofig import  params
import sys
import psutil
import operator
import multiprocessing
import  plotly  as py
import statistics
import plotly.graph_objs as go
class PartitioningManager:
    def __init__(self, k, distType):
        self.desinations = {}
        self.sources = {}
        self.n = 0
        self.path = 'sc2020/'
        self.k = k
        self.maxRuns = runs
        self.maranzana = Maranzana.Maranzana(k, distType)
        self.tb = None
        self.myopic = Myopic.Myopic(k,distType)
        self.gria = GRIA.GRIA(k, distType)
        self.em = EM.EM(k,distType)
        self.mip = MIP.MIP(k, distType)
        self.distType = distType
        self.averageDB = {}
        self.averageDunn = {}
        #self.output = 'synthetic_' + str(params['totalPopulation'])  + syntheticParams['DestinationsTable'][self.distType] + syntheticParams['DestinationsTable']['Suffix'] + "k_"+ str(self.k) + '_' + params['analysisType']



    def tbRuns(self):
        print("Let the TB GAMES BEGIN!!!! \n")
        data = []
        minSources = {}
        minCost = sys.maxsize
        for i in range(runs):
            print("Runs = "+ str(i))
            self.tb = TeitzBart.TeitzBart(self.k, self.distType)
            self.tb.getAllDestinations()
            self.tb.buildDistanceMap()
            self.tb.tbStuff()

            cost = self.tb.calculateCurrentCost()
            print(" cost = " + str(cost))
            row = [i, cost, self.tb.iterations]

            data.append(row)
            if (minCost > cost):
                minCost = cost
                minSources = dict(self.tb.currentSources)
            i += 1
        self.tb.currentSources = dict(minSources)
        self.tb.doCurrentAssignment()
        self.tb.saveDestToSourceMapping()
        print("Final Solution, cost = " + str(minCost))
        self.writeToCsv(data, self.path + '/TB/' + self.output+'.csv')

    def runMaranzanaForDecomposition(self):
        validMaranzana = Maranzana.Maranzana(self.distType, self.k)
        self.maranzana.getAllDestinations()
        #self.maranzana.buildDistanceMap()
        minCost = sys.maxsize
        maxDunn = -1
        data = []
        totalIterations = 0
        totalDB = 0
        totalDunn = 0
        for i in range(maranzanaValidityRuns):
            #print("Run  " + str(i))
            self.maranzana.iterations = 0
            self.maranzana.kMeansStuffActual()
            cost = self.maranzana.calculateCurrentCostActual()
            db = self.maranzana.measureQualityDaviesBouldin()
            dunn = self.maranzana.measureQualityDunn()
            #print(" cost = " + str(cost))
            row = [i, cost, self.maranzana.iterations]
            #self.maranzana.saveDestToSourceMapping("run_"+str(i))
            totalIterations+= self.maranzana.iterations
            totalDB+= db
            totalDunn+=dunn
            if maxDunn < dunn:
                maxDunn = dunn
                self.maranzana.minSources = dict(self.maranzana.currentSources)


            if(minCost > cost):
                minCost = cost
                self.maranzana.minSources = dict(self.maranzana.currentSources)
            self.maranzana.currentSources ={}
            self.maranzana.currentDestinationToSourceMapping ={}
            #data.append(row)
        self.averageDB[self.k] = totalDB/runs
        self.averageDunn[self.k] = totalDunn/runs

        #print("Iterations = " + str(int(totalIterations/runs)))
        #print("Final Solution, cost = " + str(minCost))
        #self.maranzana.printMinSolution()
        #self.maranzana.updateCostForMinSolution()
        self.maranzana.currentSources = dict(self.maranzana.minSources)
        self.maranzana.doCurrentAssignmentActual()
        #self.maranzana.saveDestToSourceMapping("")

        #self.writeToCsv(data, self.path+'/Maranzana/' + self.output+'.csv')

    def runMaranzanaAfterPIsKnown(self):

        self.maranzana.getAllDestinations()
        #self.maranzana.buildDistanceMap()
        # print("Run  " + str(i))
        self.maranzana.iterations = 0
        self.maranzana.kMeansStuffActual()
        self.maranzana.doCurrentAssignmentActual()
        # self.maranzana.saveDestToSourceMapping("")

        # self.writeToCsv(data, self.path+'/Maranzana/' + self.output+'.csv')


    def runMaranzana(self):
        if len(self.maranzana.destinations) ==0:
            self.maranzana.getAllDestinations()
        self.maranzana.buildDistanceMap()
        minCost = sys.maxsize
        maxDunn = -1
        data = []
        totalIterations = 0
        totalDB = 0
        totalDunn = 0
        runs = 1
        for i in range(runs):
            #print("Run  " + str(i))
            self.maranzana.iterations = 0
            self.maranzana.kMeansStuff()
            cost = self.maranzana.calculateCurrentCost()
            #print(" cost = " + str(cost))
            row = [i, cost, self.maranzana.iterations]
            #self.maranzana.saveDestToSourceMapping("run_"+str(i))
            totalIterations+= self.maranzana.iterations

            if(minCost > cost):
                minCost = cost
                self.maranzana.minSources = dict(self.maranzana.currentSources)

            data.append(row)
        self.averageDB[self.k] = totalDB/runs
        self.averageDunn[self.k] = totalDunn/runs

        #print("Iterations = " + str(int(totalIterations/runs)))
        #print("Final Solution, cost = " + str(minCost))
        #self.maranzana.printMinSolution()
        self.maranzana.updateCostForMinSolution()
        self.maranzana.currentSources = dict(self.maranzana.minSources)
        self.maranzana.doCurrentAssignment()
        #self.maranzana.saveDestToSourceMapping("")

        #self.writeToCsv(data, self.path+'/Maranzana/' + self.output+'.csv')


    def runTeitzAndBart(self, data):

        i=1
        while i<2:
            self.tb.iterations = 0
            #print("Run  " + str(i))
            self.tb.tbStuff()

        #self.tb.saveResultsToDatabase()
        #self.writeToCsv(data, self.path + 'denton_tb_70.csv')

    def runMyopic(self):
        self.myopic.getAllDestinations()
        self.myopic.buildDistanceMap()
        cost = self.myopic.myopicAlgo()
        print("Solution Cost " + str(cost))
        self.myopic.saveDestToSourceMapping()
        data = [[0, cost]]
        self.writeToCsv(data, self.path + '/Myopic/' + self.output+'_reduced.csv')




    def runMyopicMaranzanHybrid(self):
        print("------------------------------------------------HYBRID Myopic Maranzana !!!!!!!!-----------------------------------")
        self.runMyopic()
        self.maranzana.getAllDestinations()
        self.maranzana.buildDistanceMap()
        self.maranzana.kMeansWithInitialSources(self.myopic.currentSources)
        self.maranzana.minSources = dict(self.maranzana.currentSources)
        print(" Hybrid Cost = " + str(self.maranzana.calculateCurrentCost()))


    def runMyopicTBHybrid(self):
        print("------------------------------------------------HYBRID Myopic Maranzana !!!!!!!!-----------------------------------")
        self.runMyopic()
        self.tb.getAllDestinations()
        self.tb.buildDistanceMap()
        self.tb.tbStuffWithInitialSources(self.myopic.currentSources)
        self.tb.minSources = dict(self.tb.currentSources)
        print(" Hybrid Cost = " + str(self.tb.calculateCurrentCost()))


    def runGria(self) :
        print(" ~~~~~~~~~ GRIA ~~~~~~~~~~~~~ ")
        #self.gria.getAllDestinations()
        self.gria.buildDistanceMap()
        data = []
        #self.gria.initializeCurrentSources(self.maranzana.currentSources)

        self.maxRuns = 25
        runs = griaRuns
        minCost = sys.maxsize
        if len(self.gria.currentSources) > 0:
            runs = 1
        for i in range(runs):
            #self.gria.initializeCurrentSources(self.myopic.currentSources)
            #print("Run  " + str(i))
            self.gria.griaStuffParallel()
            cost = self.gria.calculateCurrentCost()
            row = [i, cost, self.gria.iterations, self.gria.globalSwapCount, self.gria.localSwapCount] # cost iterations globalswaps localswaps
            #print(" cost = " + str(cost))
            if (minCost > cost):
                minCost = cost
                self.gria.minSources = dict(self.gria.currentSources)
            data.append(row)

        #print("Final Solution, cost = " + str(minCost))
        self.gria.currentSources = dict(self.gria.minSources)
        self.gria.doCurrentAssignment(self.gria.currentSources)

        #self.gria.saveDestToSourceMapping()
        #self.writeToCsv(data, self.path + '/GRIA/' + self.output+'iterationCount.csv')

    def runGriaLocalOnly(self):
        print("Final GRIA ")
        if len(self.gria.currentSources) > 0:
            runs = 1
        for i in range(runs):
            # self.gria.initializeCurrentSources(self.myopic.currentSources)
            # print("Run  " + str(i))
            self.gria.griaStuffLocal()
            cost = self.gria.calculateCurrentCost()

        self.gria.doCurrentAssignment(self.gria.currentSources)

    def runGriaGlobalOnly(self):
        print("Final GRIA ")
        if len(self.gria.currentSources) > 0:
            runs = 1
        for i in range(runs):
            # self.gria.initializeCurrentSources(self.myopic.currentSources)
            # print("Run  " + str(i))
            self.gria.griaStuffGlobal()
            cost = self.gria.calculateCurrentCost()
        self.gria.doCurrentAssignment(self.gria.currentSources)

        # self.gria.saveDestToSourceMapping()
        # self.writeToCsv(data, self.path + '/GRIA/' + self.output+'iterationCount.csv')

    def writeToCsv(self, data, name):
        with open(name, 'w') as f:
            #print('wrting to csv')
            writer = csv.writer(f)
            writer.writerows(data)



    def getPopulationData(self):
        self.maranzana.getAllDestinations()
        data = []
        for d in self.maranzana.destinations:
            dest = self.maranzana.destinations[d]
            data.append(dest.demand)
        return data

    def plotPopulationaDistributions(self, dataList):
        trace1 = go.Histogram(x=dataList, name='random', opacity=0.55)
        data = [trace1]
        layout = go.Layout(title='Denver Population')
        fig = go.Figure(data=data, layout=layout)
        py.offline.plot(fig, filename= 'denver.html')

    def evaluateP(self, scoreDictionary):
        minResults = {}
        bestBic = sys.maxsize
        bestAic = sys.maxsize
        bestSil = -1
        bestCh = -1
        bestDB = sys.maxsize
        finalResults = {}
        for p in scoreDictionary:
            if bestBic > scoreDictionary[p]['bic']:
                bestBic = scoreDictionary[p]['bic']
                minResults['bic'] = p
            if bestAic > scoreDictionary[p]['aic']:
                bestAic = scoreDictionary[p]['aic']
                minResults['aic'] = p
            if bestSil < scoreDictionary[p]['silhouette']:
                bestSil = scoreDictionary[p]['silhouette']
                minResults['silhouette'] = p
            if bestCh < scoreDictionary[p]['calinski_harabasz']:
                bestCh = scoreDictionary[p]['calinski_harabasz']
                minResults['calinski_harabasz'] = p
            if bestDB > scoreDictionary[p]['davies_bouldin']:
                bestDB = scoreDictionary[p]['davies_bouldin']
                minResults['davies_bouldin'] = p
        # print()
        # finalResults['densityEstimates'] = int(statistics.mean([minResults['bic'], minResults['aic']]))
        finalResults['densityEstimates'] = minResults['bic']
        finalResults['clustering'] = minResults['silhouette']
        finalResults['clustering'] = int(statistics.median([minResults['silhouette'], minResults['calinski_harabasz'], minResults['davies_bouldin']]))
        finalResults['clustering'] = minResults['davies_bouldin']
        print(minResults)
        print(finalResults)
        return finalResults

    def createAndRunFIInstances(self):
        numOfProcesses = 12
        if self.em.k < numOfProcesses:
            numOfProcesses = self.em.k
        fi_instances = {}
        for s,src in self.em.currentSources.items():
            #print(str(s)+ " has :" + str(len(src.destinations)))
            label = src.label
            if fi_instances.get(label) is None:
                fi_instances[label] = FI.FastInterchange(1, self.distType)
            else :
                fi_instances[label].k+=1
            nxtSrc = len(fi_instances[label].currentSources) +1
            fi_instances[label].currentSources[nxtSrc] = src
            fi_instances[label].currentSources[nxtSrc].id = nxtSrc

            for d in src.destinations:
                fi_instances[label].destinations[d.id] = d
        ts = 0
        td = 0
        print(list(fi_instances.keys()))
        print("Number of fi to solve" +  str(self.em.k) + " or " + str(len(fi_instances)))
        for fid, obj in fi_instances.items():
            ts+= len(obj.currentSources)
            td+= len(obj.destinations)
        print("ts = " +  str(ts))
        print("td = " +  str(td))
        processGriaDictionary = {}
        for g in fi_instances:
            procId = g%numOfProcesses
            #print("chocsen process " + str(procId))
            if processGriaDictionary.get(procId) is None:
                processGriaDictionary[procId] = []
            processGriaDictionary[procId].append(fi_instances.get(g))

        procs = []
        manager = multiprocessing.Manager()
        return_dict1 = manager.dict()
        print(list(processGriaDictionary.keys()))
        print("nop = " + str(numOfProcesses))
        if __name__ == __name__:
            for i in list(processGriaDictionary.keys()):
                # print("process " + str(i) + " got "+ str(len(processGriaDictionary[i])) + " problem instances " )
                p = multiprocessing.Process(target=self.runGriaInstances, args=(processGriaDictionary[i], i, return_dict1))
                procs.append(p)
                p.start()
                # print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                # p.join()
    
            for p in procs:
                p.join()
        allSources = []
        for p in procs:
            p.terminate()
        for k in return_dict1:
            kSelectedDestinations = return_dict1.get(k)
            for d in kSelectedDestinations:
                allSources.append(d)

        print(" Total selected destinations = " + str(len(allSources)))
        return allSources


    def assignPartsToProcessesForMIP(self, parts):
        print("ASSIGNING Independenet PROBLEMs TO MIP OR FI")
        ncpus = multiprocessing.cpu_count()
        print("\n\n Number og cpus = " + str(ncpus) + "\n\n")
        numOfProcesses = 6
        if numOfProcesses > len(parts):
            numOfProcesses = len(parts)
        processMipDictionary = {}
        processGriaDictionary = {}
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        mipInstances = {}
        griaInstances = {}
        mindex = 0
        gindex = 0
        ts  = 0
        fits = 0
        for p in parts:
            part = parts.get(p)
            if len(part.destinations) <=500 or part.k<200:
                mipInstance = MIP.MIP(part.k, self.distType )
                ts+= part.k
                for d in part.destinations:
                    mipInstance.destinations[d.id] = d
                mipInstance.n = len(mipInstance.destinations)
                mipInstances[mindex] = mipInstance
                mindex+=1
            else:
                griaInstance = FI.FastInterchange(part.k, self.distType)
                fits += part.k
                for d in part.destinations:
                    griaInstance.destinations[d.id] = d
                griaInstances[gindex] = griaInstance
                gindex += 1
                
        print("Mip sources" + str(ts))
        print("FI sources" + str(fits))
        tot = ts + fits
        if tot!= params['k']:
            exit(0)
        print(tot)

        print(" Number of mip instamces " + str(len(mipInstances)))
        print(" Number of fi instamces " + str(len(griaInstances)))
        print(" Number of processes " + str(numOfProcesses))
        if numOfProcesses > len(mipInstances):
            numOfProcesses = len(mipInstances)
        for g in mipInstances:
            procId = g%numOfProcesses
            #print("chocsen process " + str(procId))
            if processMipDictionary.get(procId) is None:
                processMipDictionary[procId] = []
            processMipDictionary[procId].append(mipInstances.get(g))
        numOfProcesses = 10
        for g in griaInstances:
            procId = g%numOfProcesses
            #print("chocsen process " + str(procId))
            if processGriaDictionary.get(procId) is None:
                processGriaDictionary[procId] = []
            processGriaDictionary[procId].append(griaInstances.get(g))
        # Run mip parallely
        print("Running mip ones " + str(len(mipInstances)))
        numOfProcesses = 6
        if numOfProcesses > len(mipInstances):
            numOfProcesses = len(mipInstances)
        procs = []
        print()
        #numOfProcesses = 2
        print(processMipDictionary.keys())
        if __name__ == __name__:
            for i in range(numOfProcesses):
                print("process " + str(i) + " got "+ str(len(processMipDictionary[i])) + " problem instances " )
                
                p = multiprocessing.Process(target=self.runMipInstances,args=(processMipDictionary[i], i, return_dict))
                procs.append(p)
                p.start()
                # print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                # p.join()

            for p in procs:
                p.join()
        
        allSources = []
        for k in return_dict:
            kSelectedDestinations = return_dict.get(k)
            for d in kSelectedDestinations:
                allSources.append(d)
     
            
        manager1 = multiprocessing.Manager()
        return_dict1 = manager1.dict()
        print("Running gria ones " + str(len(griaInstances)))
        numOfProcesses = 10
        if numOfProcesses > len(griaInstances):
            numOfProcesses = len(griaInstances)
        '''
        print("Running gria ones iteratively but each has powers" + str(len(griaInstances)))
        sourcesForThisProcess = []
        for g in griaInstances:
            griaObject = griaInstances.get(g)
            minCost = sys.maxsize
            # print("Total runs for this instance " + str(runs))
            for j in range(runs):
                # self.gria.initializeCurrentSources(self.myopic.currentSources)
                # print("* Process " + str(i)+  " GRIA Run  " + str(j))
                griaObject.buildDistanceMap()
                griaObject.griaStuffParallel()
                cost = griaObject.calculateCurrentCost()
                # print(" my current sources " + str(len(griaObject.currentSources)))
                if (minCost > cost):
                    # print("changing min Sources")
                    minCost = cost
                    griaObject.minSources = dict(griaObject.currentSources)
    
            # print("Final Solution, cost = " + str(minCost))
            # print("Min sources " + str(len(griaObject.minSources)))
            griaObject.currentSources = dict(griaObject.minSources)
            for s in griaObject.currentSources:
                # print(str(s))
                source = griaObject.currentSources.get(s)
                sourcesForThisProcess.append(source.destinationId)
                allSources.append(source.destinationId)
        '''
        procs = []
        print(processGriaDictionary.keys())
        print("nop = " + str(numOfProcesses))
        if __name__ == __name__:
            for i in list(processGriaDictionary.keys()):
                # print("process " + str(i) + " got "+ str(len(processGriaDictionary[i])) + " problem instances " )
                p = multiprocessing.Process(target=self.runGriaInstances, args=(processGriaDictionary[i], i, return_dict1))
                procs.append(p)
                p.start()
                # print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                # p.join()
    
            for p in procs:
                p.join()

        for k in return_dict1:
            kSelectedDestinations = return_dict1.get(k)
            for d in kSelectedDestinations:
                allSources.append(d)

        print(" Total selected destinations = " + str(len(allSources)))
        return allSources







    def assignPartsToProcesses(self, parts):
        numOfProcesses = 5
        if numOfProcesses > len(parts):
            numOfProcesses = len(parts)
        processGriaDictionary = {}
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        griaInstances = {}
        gindex = 1
        for p in parts:
            part = parts.get(p)
            griaInstance = GRIA.GRIA(part.k, self.distType )
            for d in part.destinations:
                griaInstance.destinations[d.id] = d
            griaInstances[gindex] = griaInstance
            gindex+=1
        print(" Number of gria instamces " + str(len(griaInstances)))
        print(" Number of processes " + str(numOfProcesses))
        for g in griaInstances:
            procId = g%numOfProcesses
            #print("chocsen process " + str(procId))
            if processGriaDictionary.get(procId) is None:
                processGriaDictionary[procId] = []
            processGriaDictionary[procId].append(griaInstances.get(g))
        procs = []
        if __name__ == __name__:
            for i in range(numOfProcesses):
                #print("process " + str(i) + " got "+ str(len(processGriaDictionary[i])) + " problem instances " )
                p = multiprocessing.Process(target=self.runGriaInstances,args=(processGriaDictionary[i], i, return_dict))
                procs.append(p)
                p.start()
                # print("starting process " + str(p.pid) + " num of assigned sources " + str(len(processSourceDictionary[i])))
                # p.join()

            for p in procs:
                p.join()
        allSources = []
        for k in return_dict:
            kSelectedDestinations = return_dict.get(k)
            for d in kSelectedDestinations:
                allSources.append(d)
        print(" Total selected destinations = " + str(len(allSources)))
        return allSources

    def runMipInstances(self, mipInstances, i, return_dict):
        sourcesForThisProcess = []
        for mipObject in mipInstances:
            print("\n")
            mipObject.buildDistanceMap()
            cost = mipObject.pmedian()
            print("\n******************Cost for this instance  = "+ str(cost) + "*****************************************\n")
            for s in mipObject.currentSources:
                source = mipObject.currentSources.get(s)
                sourcesForThisProcess.append(source.destinationId)
        return_dict[i] = sourcesForThisProcess



    def runGriaInstances(self, griaInstances, i, return_dict):


        sourcesForThisProcess = []
        for griaObject in griaInstances:
            minCost = sys.maxsize
            for j in range(runs):
                # self.gria.initializeCurrentSources(self.myopic.currentSources)
                #print("* Process " + str(i)+  " GRIA Run  " + str(j))
                #griaObject.buildDistanceMap()
                griaObject.fastInterchange()
                cost = griaObject.calculateCurrentCost()
                #print(" my current sources " + str(len(griaObject.currentSources)))
                if (minCost > cost):
                    #print("changing min Sources")
                    minCost = cost
                    griaObject.minSources = dict(griaObject.currentSources)

                # print("Final Solution, cost = " + str(minCost))
            #print("Min sources " + str(len(griaObject.minSources)))
            griaObject.currentSources = dict(griaObject.minSources)
            for s in griaObject.currentSources:
                #print(str(s))
                source = griaObject.currentSources.get(s)
                sourcesForThisProcess.append(source.destinationId)
        #print("process " + str(i) + " got " + str(len(sourcesForThisProcess)) + " sources!!! " )
        return_dict[i] = sourcesForThisProcess
        #print("total selected sources " + str(return_dict[i]))
        #rint("proc id " + str(i) + " selected sources " + str(return_dict[i]))






