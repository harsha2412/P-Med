from Cofig import connectionString
from Cofig import sourceTable
from Cofig import candidateSourceGeometryTable
from shapely.geometry import Point
from Cofig import destinationDemandTable
from Cofig import destinationGeometryTable
from Cofig import candidateSourceCapacityTable
from Cofig import schemaName,params, syntheticParams
from Cofig import workingCopySchemaName
import psycopg2
import psycopg2.extras

class SourceDAO:
    def __init__(self, k, distType, method):
        self.k = k
        self.connection = psycopg2.connect(connectionString)
        self.distType = distType
        self.method = method

    def createSourceTable(self, tablename):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        deleteQuery = " DROP TABLE IF EXISTS " + schemaName + "." + self.prefix + sourceTable['Suffix'] + '_' + tablename  +";"
        print(deleteQuery)
        try:
            cursor.execute(deleteQuery)
            self.connection.commit()
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The source table could not be deleted")
            print(error.pgerror)
        query = "CREATE TABLE " + schemaName + "." + self.prefix + sourceTable['Suffix'] + '_' + tablename + "( " + sourceTable['Id'] + " integer ,  " + sourceTable['DestinationId'] + " integer, " + sourceTable['Lat'] + " Numeric, " + sourceTable['Long'] + " Numeric, " + sourceTable['Boundary'] + " Geometry, " + sourceTable['Centroid'] + " Geometry, " + sourceTable['Destinations'] + " Integer[], "  + sourceTable['Cost'] + " Numeric ); "
        print("creating source table ")
        print(query)
        try:
            cursor.execute(query)
            self.connection.commit()
        except psycopg2.Error as error:
            self.connection.rollback()
            print("The source table could not be created")
            print(error.pgerror)

    def initializeSources(self):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT  ST_Y(ST_TRANSFORM(" + candidateSourceGeometryTable['CentroidColumn'] + ",2163)) as y ,  ST_X(ST_TRANSFORM(" + candidateSourceGeometryTable['CentroidColumn'] + ",2163))  as x, " +  candidateSourceGeometryTable['Id'] + " as destinationId FROM " + workingCopySchemaName + "." + self.prefix + candidateSourceGeometryTable['Suffix'] + " ORDER BY RANDOM() limit " + str(self.k) + ";"
        print("Getting k random sources")
        print(query)
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            self.connection.commit()
            if(rows is not None):
                print("I worked !!")
                print(rows[0]['x'])
            else:
                print(" I guess I didnt ")
            return rows
        except psycopg2.Error as error:
            print("Pods table could not be initialized ")
            print(error.pgerror)
            self.connection.rollback()

    def populateSourceTable(self, sourceDictionary, tablename):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        values = "INSERT INTO " +  schemaName + "." + self.prefix + sourceTable['Suffix'] + '_' + tablename  + "(" + sourceTable['Id'] + ", " +  sourceTable['DestinationId'] + ", " + sourceTable['Lat'] + ", " + sourceTable['Long'] +  ", " + sourceTable['Centroid'] + ", " + sourceTable['Destinations'] +  ", "  + sourceTable['Cost'] + ") VALUES"
        for sid in sourceDictionary:
            source = sourceDictionary.get(sid)
            # print("Dest coordinateds")
            # print("x = " + str(source.x))
            # print("y = " + str(source.y))
            # print("Weighted Coordinates ")
            # print("x = " + str(source.weightedx))
            # print("y = " + str(source.weightedy))
            # print("Actual Coordinates ")
            # print("x = " + str(source.ax))
            # print("y = " + str(source.ay))
            dest = "ARRAY["
            cost = 0.0
            for d in source.destinations:
                 dest += str(d.id) + ","
                 #cost+=
            dest = dest[:-1]
            dest += "]"
            values+="(" + str(source.id) + ", " + str(source.destinationId) + ", " + "ST_Y(ST_SetSRID(ST_MakePoint(" + str(source.x) + "," + str(source.y) + "), 4269)), ST_X(ST_SetSRID(ST_MakePoint(" + str(source.x) + "," + str(source.y) + "), 4269)), ST_SetSRID(ST_MakePoint(" + str(source.x) + "," + str(source.y) + "), 4269), " + dest + ", " + str(source.cost) + "),"
        values = values[:-1]

        print(values)
        try:
            cursor.execute(values)
            rows = cursor.rowcount
            print("Affetced rows " + str(rows))
            self.connection.commit()
        except psycopg2.Error as error:
            print("Pods table could not be populated ")
            print(error.pgerror)
            self.connection.rollback()


    def saveSourcesReal(self, destToSourceMap, destinations,trial=0, run=""):
        # run = "local"
        run += str(trial)
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        prefix = self.distType
        tableName = workingCopySchemaName + "." + prefix + "_sources_density_k_" + str(self.k) + "_run_" + run
        caTableName = workingCopySchemaName + "." + prefix + "_ca_density_k_" + str(self.k) + "_run_" + run
        deleteTable = 'DROP TABLE IF EXISTS ' + tableName
        deleteCaTable = 'DROP TABLE IF EXISTS ' + caTableName
        createTable = 'CREATE TABLE ' + tableName + '  (destinationid integer, sourceid integer, des_centroid geometry(POINT, 2163), source_centroid geometry(POINT, 2163))'
        print(createTable)
        try:
            cursor.execute(deleteTable)
            cursor.execute(deleteCaTable)
            cursor.execute(createTable)
            for destid in destToSourceMap:
                dest = destinations.get(destid)
                insert = "INSERT INTO " + tableName + " VALUES (%(did)s, %(sid)s, ST_GeomFromWKB(%(dcentroid)s::geometry, 2163), ST_GeomFromWKB(%(scentroid)s::geometry, 2163) );"
                cursor.execute(insert, {'did': destid, 'sid': destToSourceMap[destid],
                                        'dcentroid': Point(destinations.get(destid).x,
                                                           destinations.get(destid).y).wkb_hex,
                                        'scentroid': Point(destinations.get(destToSourceMap[destid]).x,
                                                           destinations.get(destToSourceMap[destid]).y).wkb_hex})
                self.connection.commit()
            self.connection.commit()
            destTableName = workingCopySchemaName + "." + prefix + destinationGeometryTable['Suffix']
            catchmentAreasQuery = "WITH all_data as (SELECT  g.geom, s.destinationid, s.sourceid FROM " + tableName + " s, " + destTableName + " g where g.replan_id = s.destinationid) SELECT data.sourceid, ST_UNION(data.geom) as geom INTO " + caTableName + " FROM all_data data GROUP by sourceid "
            print(catchmentAreasQuery)
            cursor.execute(catchmentAreasQuery)
            self.connection.commit()
        except psycopg2.Error as error:
            print("Alas!! sources could not be saved")
            print(error.pgerror)
            self.connection.rollback()

    def createCatchmentAreas(self, sourceDictionary, tablename):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        for sid in sourceDictionary:
            source = sourceDictionary.get(sid)
            dest = "("
            cost = 0.0
            for d in source.destinations:
                dest += str(d.id) + ","
            dest = dest[:-1]
            dest += ")"
            query = "UPDATE  " + schemaName + "." + self.prefix + sourceTable['Suffix'] + '_' + tablename  + " SET " + sourceTable['Boundary']  + " =  ST_Union(ARRAY(SELECT "+  candidateSourceGeometryTable['BoundaryColumn'] + " FROM " + workingCopySchemaName + "." + self.prefix + candidateSourceGeometryTable['Suffix']  + " WHERE " + candidateSourceGeometryTable['Id'] + " IN " + dest + ")) WHERE " + sourceTable['Id'] + " = " + str(sid) + ";"
            print(query)
            centroidQuery = "UPDATE  " + schemaName + "." + self.prefix + sourceTable['Suffix'] + '_' + tablename  + " source SET (" + sourceTable['Centroid'] + ", " + sourceTable['Lat']  + ", " + sourceTable['Long'] + ") = (SELECT "  +  candidateSourceGeometryTable['CentroidColumn'] + ",  ST_Y(ST_TRANSFORM(" + candidateSourceGeometryTable['CentroidColumn'] + ",4269)), ST_X(ST_TRANSFORM(" + candidateSourceGeometryTable['CentroidColumn'] + ",4269)) FROM " + workingCopySchemaName + "." + self.prefix + candidateSourceGeometryTable['Suffix']  + " dest WHERE dest." + candidateSourceGeometryTable['Id'] + "= source." + sourceTable['DestinationId'] +  ") WHERE source." + sourceTable['Id'] + " = " + str(sid) + ";"
            print(centroidQuery)
            try:
                cursor.execute(query)
                rows = cursor.rowcount
                self.connection.commit()
            except psycopg2.Error as error:
                print("Pods table boundaries could not be updated for  pod " + str(sid) )
                print(error.pgerror)
                self.connection.rollback()
            try:
                cursor.execute(centroidQuery)
                rows = cursor.rowcount
                self.connection.commit()
            except psycopg2.Error as error:
                print("Pods table centroids could not be updated for  pod " + str(sid))
                print(error.pgerror)
                self.connection.rollback()


    def saveSources(self, destToSourceMap, destinations,trial, run):
        #run = "local"
        run += "_"+str(trial)
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        prefix = 'n_' + str(params['blockgroups'])
        numberOfCenters = params['MultiCenters']['number']
        if self.distType=="Random":
            numberOfCenters = ""
        tableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(numberOfCenters) + "_sources_dmip_k_" + str(self.k) + "_run_"+ run
        caTableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(numberOfCenters) + "_ca_dmip_k_" + str(self.k) + "_run_"+ run
        deleteTable = 'DROP TABLE IF EXISTS ' + tableName
        deleteCaTable =  'DROP TABLE IF EXISTS ' + caTableName
        createTable = 'CREATE TABLE ' + tableName + '  (destinationid integer, sourceid integer, des_centroid geometry(POINT, 2163), source_centroid geometry(POINT, 2163))'
        print(createTable)
        try:
            cursor.execute(deleteTable)
            cursor.execute(createTable)
            cursor.execute(deleteCaTable)
            for destid in destToSourceMap:
                dest = destinations.get(destid)
                insert = "INSERT INTO " + tableName +  " VALUES (%(did)s, %(sid)s, ST_GeomFromWKB(%(dcentroid)s::geometry, 2163), ST_GeomFromWKB(%(scentroid)s::geometry, 2163) );"
                cursor.execute(insert, {'did': destid, 'sid': destToSourceMap[destid],'dcentroid': Point(destinations.get(destid).x,destinations.get(destid).y).wkb_hex, 'scentroid': Point(destinations.get(destToSourceMap[destid]).x,destinations.get(destToSourceMap[destid]).y).wkb_hex})
                self.connection.commit()
            self.connection.commit()
            destTableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(numberOfCenters)+ syntheticParams['DestinationsTable']['Suffix']
            catchmentAreasQuery = "WITH all_data as (SELECT  g.geom, s.destinationid, s.sourceid FROM " +  tableName + " s, " + destTableName + " g where g.id = s.destinationid) SELECT data.sourceid, ST_UNION(data.geom) as geom INTO " + caTableName + " FROM all_data data GROUP by sourceid "
            print(catchmentAreasQuery)
            cursor.execute(catchmentAreasQuery)
            self.connection.commit()

        except psycopg2.Error as error:
                print("Alas!! sources could not be saved")
                print(error.pgerror)
                self.connection.rollback()

    def saveParts(self, partToDestinationMap, destinations, numOfParts):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        prefix = 'n_' + str(params['blockgroups'])
        numberOfCenters = params['MultiCenters']['number']
        tableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(numberOfCenters) + "_parts_" + str(numOfParts) +"_run_"+ str(params['trial'])
        deleteTable = 'DROP TABLE IF EXISTS ' + tableName
        createTable = 'CREATE TABLE ' + tableName + '  (destinationid integer, sourceid integer, des_centroid geometry(POINT, 2163), source_centroid geometry(POINT, 2163))'
        print(createTable)
        try:
            cursor.execute(deleteTable)
            cursor.execute(createTable)
            for destid in partToDestinationMap:
                dest = destinations.get(destid)
                insert = "INSERT INTO " + tableName + " VALUES (%(did)s, %(sid)s, ST_GeomFromWKB(%(dcentroid)s::geometry, 2163), ST_GeomFromWKB(%(scentroid)s::geometry, 2163) );"
                cursor.execute(insert, {'did': destid, 'sid': partToDestinationMap[destid],
                                        'dcentroid': Point(destinations.get(destid).x,
                                                           destinations.get(destid).y).wkb_hex,
                                        'scentroid': Point(destinations.get(partToDestinationMap[destid]).x,
                                                           destinations.get(partToDestinationMap[destid]).y).wkb_hex})
                self.connection.commit()
            self.connection.commit()
        except psycopg2.Error as error:
            print("Alas!! sources could not be saved")
            print(error.pgerror)
            self.connection.rollback()

    def savePartBoundaries(self, destToSourceMap, run="nonMergedParts"):
        # run = "local"
        run += str(params['trial'])
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        prefix = 'n_' + str(params['blockgroups'])
        numberOfCenters = params['MultiCenters']['number']
        tableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(
            numberOfCenters) + "_nonmergedparts_" + "run_" + str(params['trial'])
        caTableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(numberOfCenters) + "_nmp_silhoutte_" + "run_" + str(params['trial'])
        deleteTable = 'DROP TABLE IF EXISTS ' + tableName
        deletePartsTable = 'DROP TABLE IF EXISTS ' + caTableName
        createTable = 'CREATE TABLE ' + tableName + '  (destinationid integer, sourceid integer)'
        print(createTable)
        try:
            cursor.execute(deleteTable)
            cursor.execute(deletePartsTable)
            cursor.execute(createTable)
            for destid in destToSourceMap:
                insert = "INSERT INTO " + tableName + " VALUES (%(did)s, %(sid)s) ;"
                #print(str(insert))
                #print(str(destid) + ": " + str(destToSourceMap[destid]))
                cursor.execute(insert, {'did': destid, 'sid': destToSourceMap[destid]})
                self.connection.commit()

            prefix = 'Pop_' + str(params['totalPopulation'])
            print("HERE \n")
            prefix = 'n_' + str(params['blockgroups'])
            numberOfCenters = params['MultiCenters']['number']
            destTableName = workingCopySchemaName + "." + prefix + syntheticParams['DestinationsTable'][self.distType] + str(
                numberOfCenters) + syntheticParams['DestinationsTable']['Suffix']

            catchmentAreasQuery = "WITH all_data as (SELECT  g.geom, s.destinationid, s.sourceid FROM " + tableName + " s, " + destTableName + " g where g.id = s.destinationid) SELECT data.sourceid, ST_UNION(data.geom) as geom INTO " + caTableName + " FROM all_data data GROUP by sourceid "
            print(catchmentAreasQuery)
            cursor.execute(catchmentAreasQuery)
            deleteSources = " DROP TABLE " + tableName
            cursor.execute(deleteSources)
            self.connection.commit()

        except psycopg2.Error as error:
            print("Alas!! sources could not be saved")
            print(error.pgerror)
            self.connection.rollback()
















