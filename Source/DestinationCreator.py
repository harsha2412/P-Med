from Distribution import  UniformDistribution, Center, MultiCenters
import matplotlib.pyplot as plt
from DAOs import DestinationDAO
from Cofig import syntheticParams, params
import csv
class DestinationCreator:
    def __init__(self, pmgrid):
        self.pmgrid = pmgrid
        wName = 'synthetic ' + str(self.pmgrid.gridSize) + '_pop' + str(self.pmgrid.population)
        #self.uniform = UniformDistribution.UniformDistribution(pmgrid)
        self.center = Center.Centered(pmgrid)
        self.mcenter = MultiCenters.MultiCenters(pmgrid)
        self.region = {}
        self.destDAO = DestinationDAO.DestinationDAO(wName)


    def createUniformDestinations(self):
        print("*************************\n\n UNIFORM \n\n")
        self.uniform.createDestinations()
        self.uniform.createRegion()
        self.region = self.uniform.region
        self.destDAO.insertDestinationsTake2(self.region,'Random' )


    def plotRegion(self):
        fig, axs = plt.subplots()
        for bid in self.region:
            b = self.region.get(bid)
            if b.boundary.__class__.__name__ == 'Polygon':
                xs,ys = b.boundary.exterior.xy
                plt.plot(xs,ys, c='b')
            plt.scatter(b.point.x, b.point.y, 15, 'g')
        plt.show()

    def createCenteredDestination(self):
        print("\n\n ONE CENTER \n\n")
        self.center.distributePopulation()
        self.center.createDestinations()
        self.center.createRegion()
        self.region = self.center.region
        self.destDAO.insertDestinationsTake2(self.region,'OneCluster')


    def createMultiClusterDestinations(self):
        #print("\n\n Two CENTERs \n\n")
        print("Creating Multi-Centered Distribution ")
        self.mcenter.distributePopulation()
        self.mcenter.createDestinations()
        self.mcenter.createRegion()
        self.region = self.mcenter.region
        self.destDAO.insertDestinationsTake2(self.region,'MultipleClusters', params['MultiCenters']['number'])

