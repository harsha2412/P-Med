#import OPTIMAL as OPTIMAL
from mip.model import *
from Model import Destination, Source
from DAOs import DestinationDAO, SourceDAO
from mip import *
import  sys
import Utilities as util
class MIP:
	def __init__(self, k, distType):
		self.p = k
		self.destinations = {}
		#self.mipExample() # example works!!
		self.dij = []
		self.destinations = {}
		self.distanceMap = {}
		self.indexToId = {}
		self.destinationDao = DestinationDAO.DestinationDAO(distType)
		self.demandWeights = []
		self.util = util.Utilities()
		self.distType = distType
		self.currentDestinationToSourceMapping = {}
		self.currentSources = {}
		self.sourceDao = SourceDAO.SourceDAO(k, distType, 'GRIA')
		self.n = 0
		#self.getAllDestinations()
		#self.buildDistanceMap()
		#self.pmedian()



	def getAllDestinations(self):
		results = self.destinationDao.getAllSyntheticDestinations(self.distType)
		for row in results:
			newDestination = Destination.Destination(row['destinationid'], row['x'], row['y'], row['demand'])
			newDestination.x = round(newDestination.x, 4)
			newDestination.y = round(newDestination.y, 4)
			self.destinations[newDestination.id] = newDestination
		self.n = len(self.destinations)

	def buildDistanceMap(self):
		index = 0
		for d1 in self.destinations:
			self.indexToId[index] = d1
			self.distanceMap[d1] = {}
			index+=1
		for i in range(self.n):
			myDistances = []
			myDestId = self.indexToId[i]
			self.demandWeights.append(self.destinations.get(myDestId).demand)
			for j in range(self.n):
				currentDest = self.indexToId[j]
				distance = self.util.calculateDistanceBetweenDestinations(self.destinations.get(myDestId), self.destinations.get(currentDest))
				myDistances.append(distance)
			self.dij.append(myDistances)

	def mipExample(self):
		m = Model()
		x = [m.add_var( lb=0) for i in range(2)]
		m += 2*x[0] + 3*x[1] >= 8
		m += 5 * x[0] + 2 * x[1] >= 12
		m.objective = 3*x[0] + 4*x[1]
		m.max_gap = 0.05


		status = m.optimize(max_seconds=300)
		print("vars" + str(m.vars[0].x) + ", " + str(m.vars[1].x))
		print("status = " + str(status))
		if status == OptimizationStatus.OPTIMAL:
			print('optimal solution cost {} found'.format(m.objective_value))
		elif status == OptimizationStatus.FEASIBLE:
			print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
		elif status == OptimizationStatus.NO_SOLUTION_FOUND:
			print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
		if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
			print('solution:')
			for v in m.vars:
				if abs(v.x) <= 1e-7:
					continue
				print('{} : {}'.format(v.name, v.x))

	def doCurrentAssignment(self):
		for s in self.currentSources:
			source = self.currentSources.get(s)
			source.destinations = []
		for d in self.destinations:
			self.currentDestinationToSourceMapping[d] = self.pickMinSource(d)

	def pickMinSource(self, destination):
		min = sys.maxsize

		minSource = 1
		minsid = -1
		for source in self.currentSources:
			sid = self.currentSources[source].id
			# print("hererre "+ str(sid))
			s = self.currentSources[source].destinationId
			if destination == s:
				minSource = s
				minsid = sid
				break
			else:
				if self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(destination)) < min:
					min = self.util.calculateDistanceBetweenDestinations(self.destinations.get(s), self.destinations.get(destination))
					minSource = s
					minsid = sid
		self.currentSources.get(minsid).destinations.append(self.destinations.get(destination))
		return minSource

	def calculateCurrentCost(self):
		cost = 0.0
		for d in self.currentDestinationToSourceMapping:
			s = self.currentDestinationToSourceMapping[d]
			cost += self.util.calculateDistanceBetweenDestinations(self.destinations.get(s),self.destinations.get(d)) * self.destinations.get(d).demand
		return cost

	def pmedian(self):
		model = Model()
		print("Problem scale " + str(self.n) + ", " + str(self.p))
		alpha = [[model.add_var(name='alpha', var_type=BINARY) for j in range(self.n)] for i in range(self.n)]
		x = [model.add_var(name='isFacility', var_type=BINARY) for i in range(self.n)]

		# constraint 1
		for i in range(self.n):
			model += xsum(alpha[i][j] for j in range(self.n) ) == 1

		# constraint 2
		for i in range(self.n):
			for j in range(self.n):
				model += alpha[i][j] - x[j] <= 0

		#constraint 3
		model += xsum(x[j] for j in range(self.n)) == self.p

		# objective function
		model.objective = minimize(xsum(self.demandWeights[i]*self.dij[i][j]*alpha[i][j] for j in range(self.n) for i in range(self.n)))
		status = model.optimize(max_seconds=360000)
		print("solution status " + str(status) )
		xj = []
		alphaij = []
		for v in model.vars:
			if v.name == "isFacility":
				xj.append(v.x)


		iIndex = 0
		sId = 1
		for k in xj:
			if int(k)==1:
				destId = self.indexToId[iIndex]
				dest = self.destinations.get(destId)
				newsource = Source.Source(dest.x, dest.y, dest.id,sId )
				self.currentSources[sId] = newsource
				sId+=1
				#print("iIndex "+ str(iIndex) + ", corresponding destination " + str(self.indexToId[iIndex]))
			iIndex +=1
		self.doCurrentAssignment()
		cost = self.calculateCurrentCost()
		print("cost (obj value) " + str(cost))
		return cost
		#print("cost (obj value) " + str(cost))


	def runPlainMIP(self):
		self.getAllDestinations()
		self.buildDistanceMap()
		self.pmedian()
		self.saveDestToSourceMapping()

	def saveDestToSourceMapping(self):
		self.sourceDao.saveSources(self.currentDestinationToSourceMapping, self.destinations, "plainmip")

		'''
		if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
			print('solution: ')
			for v in model.vars:
				print("name " + str(v.name) + "value = " + str(v.x))
		'''


