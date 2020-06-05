import sys
import collections
import random
from Cofig import  params
from DAOs import SourceDAO
from DAOs import DestinationDAO
from Model import Source
from Model import Destination
import Utilities as util
import statistics
from sklearn.datasets.samples_generator import make_blobs
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from Distribution import  NormalityTester
from sklearn import metrics
class EM:
        def __init__(self, k, distType):
                self.k = k
                self.distType = distType
                self.destinations ={}
                self.destinationData = []
                self.destinationIds = {}
                self.sourceIdToDesinationIdMap = {}
                self.sourceDao = SourceDAO.SourceDAO(k, distType, 'EM')
                self.destinationDao = DestinationDAO.DestinationDAO(distType)
                self.util = util.Utilities()
                self.totalDemandInTheRegion= 0
                self.parts = {}
                self.currentDestinationToSourceMapping = {}
                self.partToDestinationMap = {}
                self.currentSources = {}
                #self.gmmExample()
                #exit(0)

        def gmmExample(self):
                X, y_true = make_blobs(n_samples=400, centers=5,
                                                           cluster_std=0.60, random_state=0)
                #print(X)
                X = X[:, ::-1]
                #print(X)
                gmm = GaussianMixture(n_components=4).fit(X)
                val = gmm.bic(X)
                print("bic val = "+ str(val))
                labels = gmm.predict(X)
                print(str(labels))
                plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='inferno')
                plt.show()
                #print(str(X))

        def getAllDestinations(self):
                #results = self.destinationDao.getAllSyntheticDestinations(self.distType)
                results = self.destinationDao.getAllDestinations()
                index = 0
                for row in results:
                        newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
                        entry = []
                        entry.append(row['x'])
                        entry.append(row['y'])
                        self.destinationData.append(entry)
                        self.destinationIds[index] = row['destinationid']
                        self.totalDemandInTheRegion += int(row['demand'])
                        self.destinations[newDestination.id] = newDestination
                        index += 1
                self.n = len(self.destinations)
                #print(self.destinationData)
                #print("Total Number of destintions " + str(self.n))
        def clusterSources(self):
            sourceData = []
            sourceids = {}
            index = 0
            for s, src in self.currentSources.items():
                sourceData.append([src.x, src.y])
                sourceids[index] = s
                index+=1
            labels =  KMeans(n_clusters=self.k, random_state=0).fit(np.array(sourceData)).labels_
            i = 0 
            while(i<len(labels)):
                sid = sourceids[i]
                self.currentSources.get(sid).label = int(labels[i])+1
                i+=1

        def createGmmClusters(self, plotFlag=False):
                X = np.array(self.destinationData)
                # extra params for GM  tol =0.0001, max_iter=1000
                gmm = GaussianMixture(n_components=self.k).fit(X)
                labels = gmm.predict(X)
                #print(labels)
                if plotFlag:
                        i=0
                        while i<len(labels):
                                destId = self.destinationIds[i]
                                self.destinations.get(destId).label = int(labels[i])+1
                                i+=1
                        #self.createParts()


                chscore = metrics.calinski_harabasz_score(X, labels)
                dbscore = metrics.davies_bouldin_score(X, labels)
                sil_score = metrics.silhouette_score(X, labels, metric='euclidean')
                bicscore = gmm.bic(X)
                aicscore = gmm.aic(X)
                score = {}
                score['calinski_harabasz'] = chscore
                score['davies_bouldin'] = dbscore
                score['bic'] = bicscore
                score['aic'] = aicscore
                score['silhouette'] = sil_score
                '''
                print("**************")
                print("p = " + str(self.k))
                print(str(score))
                print("**************")
                '''


                #print(labels)
                if plotFlag:
                        xcor = []
                        ycor = []
                        for entry in self.destinationData:
                                xcor.append(entry[0])
                                ycor.append(entry[1])
                        plt.scatter(xcor, ycor, c=labels, s=40, cmap='inferno')
                        #plt.show()
                return score


        def plotScores(self,ps, scores):
                plt.plot(ps,scores)
                plt.show()

        def evaluateP(self, scoreDictionary):
                minResults = {}
                bestBic = sys.maxsize
                bestAic = sys.maxsize
                bestSil  = -1
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
                #print()
                #finalResults['densityEstimates'] = int(statistics.mean([minResults['bic'], minResults['aic']]))
                finalResults['densityEstimates'] = minResults['bic']
                finalResults['clustering'] = minResults['calinski_harabasz']
                #finalResults['clustering'] = int(statistics.mean([minResults['silhouette'], minResults['calinski_harabasz'], minResults['davies_bouldin']]))
                #print("hgjhgjhgjgj")
                #print(minResults)
                #print(finalResults)
                return finalResults

        def createParts(self, merge = True):
                #print("creating parts " + str(merge))
                self.parts = {}
                for d in self.destinations:
                        dest = self.destinations.get(d)
                        key = int(dest.label)
                        if self.parts.get(key) is None:
                                destArray = []
                                destArray.append(dest)
                                self.parts[key] = Part(destArray, key)
                        else:
                                self.parts.get(key).destinations.append(dest)
                print("Total Parts " + str(len(self.parts)))
                assignedFacilities = 0
                maxDemandPointPart = None
                maxdemandPoints = -1

                for k in self.parts:
                        part = self.parts.get(k)
                        part.k = self.getNumberOfFacilitiesForThisPart(part.destinations)
                        assignedFacilities += part.k
                        if part.totalDemandPoints > maxdemandPoints:
                                maxDemandPointPart = part
                                maxdemandPoints = part.totalDemandPoints
                if assignedFacilities < params['k']:
                        remaining = params['k'] - assignedFacilities
                        maxDemandPointPart.k += remaining
                        maxDemandPointPart.valid = False
                        self.parts[maxDemandPointPart.id] = maxDemandPointPart
        
                for p in self.parts:
                        #print(part.k)
                        part = self.parts.get(p)
                        part.populateCentroid()
                        self.currentSources[p] = Source.Source(part.x, part.y, -1, p)
                        ## bring me back
                        if merge:
                                part.homogeneous = self.areDemandPointsRandom(part.destinations)

                if merge:
                                self.mergePartsByDeletingSources()

                self.k = len(self.parts)
                self.sourceDao.k = self.k
                self.partToDestinationMap = {}

                for p in self.parts:
                                for d in self.parts.get(p).destinations:
                                        self.partToDestinationMap[d.id] = p

        
                #print(str(self.partToDestinationMap))

        def areDemandPointsRandom(self, dests):
                #print("Checing ramdomenss")
                boundingBox = {}
                list = "("
                for d in dests:
                        list += str(d.id) + ", "
                list = list[:-2]
                list += ")"
                rows = self.destinationDao.getBoundingBox(self.distType, list)
                boundingBox['xmin'] = rows['xmin']
                boundingBox['ymin'] = rows['ymin']
                boundingBox['xmax'] = rows['xmax']
                boundingBox['ymax'] = rows['ymax']
                # print("BB " + str(boundingBox))
                # boundingBox['x_min']= rows[0]['xmin']

                normalityTester = NormalityTester.NormalityTester(dests, self.util, boundingBox,self.destinationDao.getRegion(self.distType, list))
                
                return normalityTester.checkForNormality()

        def doCurrentAssignmentActual(self):
                for s in self.currentSources:
                        source = self.currentSources.get(s)
                        #print(" source " + str(s) + "x,y " + str(source.x) + ", " + str(source.y))
                        source.destinations = []
                for d in self.destinations:
                        self.currentDestinationToSourceMapping[d] = self.pickMinSourceBasedOnDistance(d)


        def pickMinSourceBasedOnDistance(self, destination):
                min = sys.maxsize
                minSource = 1
                minsid = -1
                #print("In picking the min source for destination " + str(destination) + ", total sources = " +  str(len(self.currentSources)))
                for source in self.currentSources:
                        sid = self.currentSources[source].id
                        src = self.currentSources.get(source)
                        #print("hererre "+ str(sid))
                        s = self.currentSources[source].destinationId
                        if self.util.calculateDistanceBetweenDestinations(src, self.destinations.get(destination)) < min:
                                min = self.util.calculateDistanceBetweenDestinations(src, self.destinations.get(destination))
                                minSource = s
                                minsid = sid
                #print("closest source "+ str(minsid))
                sourceToUpdate = self.currentSources.get(minsid)
                self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
                return minsid

        def mergePartsByDeletingSources(self):
                #print("Didi I get herer")
                deletedSources = []
                
                for s in self.parts:
                        part = self.parts.get(s)
                        if part.homogeneous or part.k ==0:
                                #print("Deleting source " + str(s))
                                deletedSources.append(s)
                #print("Number of source to delere " +str(len(deletedSources)))
                if len(deletedSources) > len(self.parts)-2:
                                self.currentSources = {}
                                return
                for s in deletedSources:
                        del self.currentSources[s]
                        #print(s)
        
                self.doCurrentAssignmentActual()
                self.createPartitionsFromSources()

        def getNumberOfFacilitiesForThisPart(self, dests):
                totalDemand = 0
                # print("Total demand in region " + str(self.totalDemandInTheRegion))
                for d in dests:
                        totalDemand += d.demand
                proportion = totalDemand / self.totalDemandInTheRegion
                # print("My prop " + str(proportion))
                kProp = int(proportion * params['k'])
                return kProp

        def createPartitionsFromSources(self):
                self.parts = {}
                assignedFacilities = 0
                maxDemandPointPart = None
                maxdemandPoints = -1
                for s in self.currentSources:
                        source = self.currentSources.get(s)
                        #print("source " + str(s) +  ", I have " + str(len(source.destinations)))
                        part = Part(source.destinations, s)
                        k = self.getNumberOfFacilitiesForThisPart(source.destinations)
                        part.k = k
                        assignedFacilities += part.k
                        self.parts[s] = part
                        if part.totalDemandPoints > maxdemandPoints:
                                maxDemandPointPart = part
                                maxdemandPoints = part.totalDemandPoints
                        # print("n = "+ str(len(part.destinations)))
                        # print("p = " + str(part.k))
                        part.homogeneous = self.areDemandPointsRandom(source.destinations)

                if assignedFacilities < params['k']:
                        remaining = params['k'] - assignedFacilities
                        maxDemandPointPart.k += remaining
                        maxDemandPointPart.valid = False
                        maxDemandPointPart.homogeneous = self.areDemandPointsRandom(maxDemandPointPart.destinations)
                        self.parts[maxDemandPointPart.id] = maxDemandPointPart
                print("Number of parts after merging " + str(len(self.parts)))

# each decomposition part
class Part:
        def __init__(self, destinations, id):
                self.destinations = destinations
                self.id = id
                self.totalDemandPoints = len(self.destinations)
                self.k = -1
                self.sources = {}  # after gria
                self.valid = False  # valid if either solvable or random
                self.homogeneous = False
                self.assigned = False
                self.parent = -1
                self.x = -1
                self.y = -1

        def printPart(self):
                print("Part " + str(self.id))
                print("Demand " + str(len(self.destinations)))
                print("Facilities to be located " + str(self.k))
                print("Is part Homogeneous " + str(self.homogeneous))

        def populateCentroid(self):
                xSum = 0
                ySum = 0
                for d in self.destinations:
                        xSum += d.x
                        ySum += d.y
                self.x = xSum/len(self.destinations)
                self.y = ySum/len(self.destinations)
