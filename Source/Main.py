import DataFetcher
import Plotter
pop = 500000
disttype = 'MulClusters80_1'
dist = "MulClusters80_1"
#disttype = 'Random'

# dist = "Random"

filename = str(pop) + '_' + disttype
path = "csvs/"
method = "Maranzana"
method2 = "TB"
method3 = "GRIA"
method4 = "Myopic"

dataFethcher = DataFetcher.DataFetcher(pop, disttype, path )
#dataFethcher.getCostData()
#dataFethcher.getTimeData()


plotter = Plotter.Plotter()
k =2
data = []
distributionData = {}
#data.append(["k", "median", "max", "min", "std", "avg"])
while k <=64:
    distributionData[k] = []
    print("*******\n")
    variationPath = "/home/harsha/PycharmProjects/weighted/resultsFinal/"+method+ "/"
    variationFile = "synthetic_" + str(pop) + "_" + dist + "_destinationsk_"+ str(k) + "_w" + ".csv"
    variationFileName = variationPath + variationFile

    variationPath1 = "/home/harsha/PycharmProjects/weighted/resultsFinal/" + method2 + "/"
    variationFile1 = "synthetic_" + str(pop) + "_" + dist + "_destinationsk_" + str(k) + "_w" + ".csv"
    variationFileName1 = variationPath1 + variationFile1

    variationPath2 = "/home/harsha/PycharmProjects/weighted/resultsFinal/GRIA/"
    variationFile2 = "synthetic_" + str(pop) + "_" + dist + "_destinationsk_" + str(k) + "_w" + ".csv"
    variationFileName2 = variationPath2 + variationFile2


    variationPath3 = "/home/harsha/PycharmProjects/weighted/resultsFinal/Myopic/"
    variationFile3 = "synthetic_" + str(pop) + "_" + dist + "_destinationsk_" + str(k) + "_w" + ".csv"
    variationFileName3 = variationPath3 + variationFile3

    dataDic = dataFethcher.getVariationData( variationFileName)
    dataDic1 = dataFethcher.getVariationData(variationFileName1)
    dataDic2 = dataFethcher.getVariationData(variationFileName2)
    dataDic3 = dataFethcher.getVariationData(variationFileName3)
    for r in dataDic2:
        distributionData[k].append(dataDic2[r])



    #rowk = [k]
    rowMaranzana = plotter.plotVariationAndCalculateVariance(str(pop) + " " + method + " " + disttype + "k = " + str(k), dataDic, method,variationFile )
    rowTB = plotter.plotVariationAndCalculateVariance(str(pop) + " " + method + " " + disttype + "k = " + str(k), dataDic1, "TB", variationFile1)
    rowGria =  plotter.plotVariationAndCalculateVariance(str(pop) + " " + method + " " + disttype + "k = " + str(k), dataDic2, "GRIA", variationFile1)
    rowMyopic = plotter.plotVariationAndCalculateVariance(str(pop) + " " + method + " " + disttype + "k = " + str(k), dataDic3, "Myopic", variationFile1)
    tbMax = rowTB[1]
    i = 0
    maranMin = rowMaranzana[2]/tbMax
    griaMax = rowGria[1]/tbMax
    myopic = rowMyopic[0]/tbMax
    rowk= [k, griaMax, myopic,maranMin ]
    data.append(rowk)
    k = k*2
print("\n\n\n\n\n*************************************************\n\n")
for r in data:
    print(r)
#print(data)
variationPath = "resultsFinal/Cumulative/"
variationFile = method+ "_synthetic_" + str(pop) + "_" + dist + "_relative_result.csv"
variationFileName = variationPath + variationFile
plotter.plotDistributionsForAllKs('GRIA Distribution',distributionData,   "GRIA_synthetic_" + str(pop) + "_" + dist + "_distribution_result.html"  )
#dataFethcher.saveAllStats(variationFileName, data)
#plotter.plotTimeAndCostWithPlotly(dataFethcher.ks, dataFethcher.maranzana_cost, dataFethcher.myopic_cost, dataFethcher.gria_cost, dataFethcher.maranzana_time, dataFethcher.myopic_time, dataFethcher.gria_time, filename, str(pop) + " , " + ' Ten Clusters')

#plotter.plotCostComparisons(dataFethcher.ks, dataFethcher.maranzana_cost, dataFethcher.myopic_cost, dataFethcher.gria_cost)