import os
import csv
class DataFetcher:
    def __init__(self, pop, distType, path):
        self.costFile = path +  distType + '_' + str(pop) + '.csv'
        self.timeFile = path + distType + '_' + str(pop) + '_time.csv'
        self.maranzana_cost = []
        self.maranzana_time = []
        self.myopic_cost = []
        self.myopic_time = []
        self.gria_cost = []
        self.gria_time = []
        #self.tb_time = []

        self.ks = []


    def getCostData(self):
        data = []
        print("Getting cost data")
        if os.path.exists(self.costFile):
            with open(self.costFile, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
        for i in range(1, len(data)):
            row = data[i]
            self.ks.append(row[0])
            self.maranzana_cost.append(row[1])
            self.myopic_cost.append(row[2])
            self.gria_cost.append(row[3])
        print(self.maranzana_cost)
        print(self.myopic_cost)
        print(self.gria_cost)


    def getTimeData(self):
        data = []
        print("Getting time data")
        if os.path.exists(self.timeFile):
            with open(self.timeFile, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
        for i in range(1, len(data)):
            row = data[i]
            #self.ks.append(row[0])
            self.maranzana_time.append(row[1])
            self.myopic_time.append(row[2])
            self.gria_time.append(row[3])
            #self.tb_time.append(row[4])
        print(self.maranzana_time)
        print(self.myopic_time)
        print(self.gria_time)
        #print(self.tb_time)

    def getVariationData(self, fileName):
        data = {}
        print(fileName)
        print("Getting run data")
        if os.path.exists(fileName):
            print("found the file ")
            with open(fileName, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    data[row[0]] = row[1]
        print(data)
        return data

    def saveAllStats(self, fileName, data):
        #head = ["k", "median", "avg", "max", "std", "min"]


        with open(fileName, 'w', newline='') as f:
            # print('wrting to csv')
            writer = csv.writer(f)
            #writer.writerows(head)
            writer.writerows(data)
