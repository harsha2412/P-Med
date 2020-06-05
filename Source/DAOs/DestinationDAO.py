from Cofig import connectionString
from Cofig import params
from Cofig import syntheticParams
from Cofig import destinationDemandTable
from Cofig import destinationGeometryTable
from Cofig import schemaName
from Cofig import workingCopySchemaName
import psycopg2
#import shapely
from shapely import wkb
import psycopg2.extras
class DestinationDAO:
    def __init__(self, workingCopyName):
        self.n = 0
        self.connection = psycopg2.connect(connectionString)
        self.prefix = workingCopyName

    def getAllDestinations(self):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = " SELECT ST_Y(ST_TRANSFORM(" + destinationGeometryTable['CentroidColumn'] + ",2163)) as y ,  ST_X(ST_TRANSFORM(" + destinationGeometryTable['CentroidColumn'] + ",2163))  as x, demand." + destinationDemandTable['Id'] + " as destinationId, demand." + destinationDemandTable['DemandColumn'] + " as demand FROM " + workingCopySchemaName + "." + self.prefix + destinationGeometryTable['Suffix'] +  " shape, " +    workingCopySchemaName + "." + self.prefix + destinationDemandTable['Suffix'] + " demand WHERE shape." + destinationGeometryTable['Id'] + " = demand." + destinationDemandTable['Id']
        #print("Getting all destination data")
        #print(query)
        try:
            cursor.execute(query)
            self.connection.commit()
            rows = cursor.fetchall()
            return rows
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The destinations could not be fetched")
            print(error.pgerror)


    def saveSyntheticDestinations(self, prefix, blockGroups):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        createTable = "CREATE TABLE IF NOT EXISTS " + workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable']['Random'] + syntheticParams['DestinationsTable']['Suffix'] + '( ' + syntheticParams['DestinationsTable']['DestinationId'] + ' Integer, ' + syntheticParams['DestinationsTable']['Boundary'] + ' geometry(MultiPolygon,2163), ' + syntheticParams['DestinationsTable']['Centroid'] + ' geometry(Point,2163),  ' +  syntheticParams['DestinationsTable']['Demand'] + ' integer' +  ')'
        insert = "INSERT INTO " +  workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable']['Random'] + syntheticParams['DestinationsTable']['Suffix'] + ' VALUES '
        print(createTable)
        for bid in blockGroups:
            bg = blockGroups.get(bid)
            row = '(' + str(bid) + ', ST_SetSRID(' + str(bg.boundary.wkb_hex) + '::geometry, 2163), ST_SetSRID(' + str(bg.point.wkb_hex) + '::geometry, 2163), ' + str(bg.demand) + '), '
            insert += row

        insert = insert[:-2]


        try:
            cursor.execute(createTable)
            self.connection.commit()
            truncate = " TRUNCATE TABLE " + workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable']['Random'] + syntheticParams['DestinationsTable']['Suffix']
            cursor.execute(truncate)
            self.connection.commit()
            cursor.execute(insert)
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The destinations could not be saved")
            print(error.pgerror)

    def insertDestinationsTake2(self, blockGroups, distType, numberOfCenters=""):
        #prefix =  str(params['totalPopulation']) + syntheticParams['DestinationsTable']['Random']
        prefix ='n_'+ str(len(blockGroups))
        cursor = self.connection.cursor(curLsor_factory=psycopg2.extras.DictCursor)
        dropTable = " DROP TABLE IF EXISTS " + workingCopySchemaName + "." + prefix + \
                      syntheticParams['DestinationsTable'][distType]+ str(numberOfCenters)  + syntheticParams['DestinationsTable'][
                          'Suffix']
        cursor.execute(dropTable)
        self.connection.commit()

        createTable = "CREATE TABLE IF NOT EXISTS " + workingCopySchemaName + "." + prefix + \
                      syntheticParams['DestinationsTable'][distType]+ str(numberOfCenters)+ syntheticParams['DestinationsTable'][
                          'Suffix'] + '( ' + syntheticParams['DestinationsTable']['DestinationId'] + ' Integer, ' + \
                      syntheticParams['DestinationsTable']['Boundary'] + ' geometry(MultiPolygon, 2163), ' + \
                      syntheticParams['DestinationsTable']['Centroid'] + ' geometry(Point,2163),  ' + \
                      syntheticParams['DestinationsTable']['Demand'] + ' integer' + ')'
        print(createTable)
        try:
            cursor.execute(createTable)
            self.connection.commit()
            truncate = " TRUNCATE TABLE " + workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][
                distType] + str(numberOfCenters)+ syntheticParams['DestinationsTable']['Suffix']
            cursor.execute(truncate)
            print("Trying Insert for " + str(len(blockGroups)))
            for bid in blockGroups:
                bg = blockGroups.get(bid)
                insert = "INSERT INTO " + workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][distType]+ str(numberOfCenters)+  syntheticParams['DestinationsTable']['Suffix'] + " VALUES (%(id)s, ST_MULTI(ST_GeomFromWKB(%(geom)s::geometry, 2163)), ST_GeomFromWKB(%(centroid)s::geometry, 2163),%(demand)s );"
                cursor.execute(insert,{'id':bid, 'geom':bg.boundary.wkb_hex, 'centroid':bg.point.wkb_hex, 'demand':bg.demand} )
                self.connection.commit()
            print("Insert Succesful for " + str(len(blockGroups)))
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The destinations could not be saved")
            print(error.pgerror)
        #cursor.close()
        self.connection.close()

    def getAllSyntheticDestinations(self, distType):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #prefix = 'Pop_' + str(params['totalPopulation'])
        prefix = 'n_' + str(params['blockgroups'])
        numberOfCenters = params['MultiCenters']['number']
        if distType == "Random":
            numberOfCenters = ""
        tableName =workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][distType] + str(numberOfCenters)+ syntheticParams['DestinationsTable']['Suffix']
        query = " SELECT " + syntheticParams['DestinationsTable']['DestinationId'] + " as destinationid, ST_Y(" + syntheticParams['DestinationsTable'][
            'Centroid'] +" ) as y ,  ST_X(" + syntheticParams['DestinationsTable']['Centroid'] +" ) x, " + syntheticParams['DestinationsTable']['Demand'] + " as demand FROM " + tableName
        #print("Getting all synthetic data destination data")
        #print(query)
        try:
            cursor.execute(query)
            self.connection.commit()
            rows = cursor.fetchall()
            return rows
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The synthetic destinations could not be fetched")
            print(error.pgerror)
        self.connection.close()


    def getEPPSolution(self):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = " SELECT  demand." + destinationDemandTable[
                    'Id'] + " as destinationId  FROM " + workingCopySchemaName + "." + self.prefix + "_"+ str(self.k) + \
                destinationDemandTable['eppSuffix'] + " demand "
        print("Getting all destination data")
        print(query)
        try:
            cursor.execute(query)
            self.connection.commit()
            rows = cursor.fetchall()
            return rows
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The destinations could not be fetched")
            print(error.pgerror)



    def getBoundingBox(self, distType, values):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        prefix = 'n_' + str(params['blockgroups'])

        numberOfCenters = params['MultiCenters']['number']
        if distType == "Random":
            numberOfCenters = ""
        tableName = workingCopySchemaName + "." + self.prefix + destinationGeometryTable['Suffix']
        
        query = "SELECT ST_XMIN(ST_EXTENT(" + syntheticParams['DestinationsTable']['Boundary'] + ")) as xmin, ST_YMIN(ST_EXTENT(" + syntheticParams['DestinationsTable']['Boundary'] + ")) as ymin, ST_XMAX(ST_EXTENT(" + syntheticParams['DestinationsTable']['Boundary'] + ")) as xmax,ST_YMAX(ST_EXTENT(" + syntheticParams['DestinationsTable']['Boundary'] + ")) as ymax  FROM " + tableName + " WHERE " +  destinationGeometryTable['Id']  + " IN  " + values
        #print(query)
        try:
            cursor.execute(query)
            self.connection.commit()
            rows = cursor.fetchone()
            #print(str(rows))
            return rows
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The synthetic destinations could not be fetched")
            print(error.pgerror)
        self.connection.close()


    def getRegion(self, distType, values):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        prefix = 'n_' + str(params['blockgroups'])
        numberOfCenters = params['MultiCenters']['number']
        if distType == "Random":
            numberOfCenters = ""
        tableName = workingCopySchemaName + "." + self.prefix + destinationGeometryTable['Suffix']
        query = "SELECT ST_UNION(" + syntheticParams['DestinationsTable']['Boundary'] + ") as geom  FROM " + tableName + " WHERE " +destinationGeometryTable['Id']  + " IN  " + values
        #print(query)
        try:
            cursor.execute(query)
            self.connection.commit()
            rows = cursor.fetchall()
            geom = wkb.loads(rows[0]['geom'], hex=True)
            #print(str(rows))
            return geom
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The synthetic destinations could not be fetched")
            print(error.pgerror)
        self.connection.close()


    def saveGridOverPart(self, cellList, region):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        deleteTable = "DROP TABLE IF EXISTS la.aa_test_grid"
        createTable = 'CREATE TABLE la.aa_test_grid (geom geometry(Polygon, 2163), region geometry(MultiPOLYGON, 2163))'
        print(createTable)
        try:
            cursor.execute(deleteTable)
            cursor.execute(createTable)
            for cell in cellList:
                #print(cell)
                insert = "INSERT INTO la.aa_test_grid" + " VALUES ( ST_GeomFromWKB(%(cellPolygon)s::geometry, 2163), ST_GeomFromWKB(%(region)s::geometry, 2163) );"
                #print(insert)
                cursor.execute(insert, {'cellPolygon': cell.wkb_hex, 'region':region.wkb_hex})
                self.connection.commit()

        except psycopg2.Error as error:
            print("Alas!! grid could not be saved!! ")
            print(error.pgerror)
            self.connection.rollback()





