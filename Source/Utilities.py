from Model import Source
from Model import Destination
import math
class Utilities:
    def __init__(self):
        self.bs = "vd"
        #print("Use Me!")
    def calculateDistanceBetweenDestinations(self, d1, d2):
        #return math.sqrt(((d1.x-d2.x)*(d1.x-d2.x)) +((d1.y-d2.y)*(d1.y-d2.y)))
        return math.sqrt(((d1.x-d2.x)*(d1.x-d2.x)) +((d1.y-d2.y)*(d1.y-d2.y)))

    def calculateDistanceBetweenDestinationsWeighted(self, d1, d2):
        #return math.sqrt(((d1.x-d2.x)*(d1.x-d2.x)) +((d1.y-d2.y)*(d1.y-d2.y)))
        return math.sqrt(((d1.x-d2.x)*(d1.x-d2.x)) +((d1.y-d2.y)*(d1.y-d2.y)))*float(d2.demand)


    def calculateDistanceBetweenPoints(self, d1, d2):
        #return math.sqrt(((d1.x-d2.x)*(d1.x-d2.x)) +((d1.y-d2.y)*(d1.y-d2.y)))
        return math.sqrt(((d1.x-d2.x)*(d1.x-d2.x)) +((d1.y-d2.y)*(d1.y-d2.y)))