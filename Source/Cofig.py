import yaml
settingsFile ="Constants.yml"
with open(settingsFile,'r') as configStream :
    data = yaml.load(configStream)
    try:
        # Database Settings
        config  = data['Database']
        connectionString ="host='" + config['Host'] + "' dbname='" + config['Name'] + "' user='" + config['User'] + "' password='" + config['Password'] + "'"
        destinationDemandTable = data['DestinationDemandTable']
        destinationGeometryTable = data['DestinationGeometryTable']
        candidateSourceCapacityTable = data['CandidateSourceCapacityTable']
        candidateSourceGeometryTable = data['CandidateSourceGeometryTable']
        sourceTable = data['SourceTable']
        schemaName = data['SchemaName']
        syntheticParams = data['SyntheticData']
        workingCopySchemaName = data['WorkingCopySchemaName']
        params = data['params']
        runs = data['Runs']
        griaRuns=  data['GriaRuns']
        maranzanaValidityRuns = data['MaranzanaValidityRuns']

    except yaml.YAMLError as exc:
        print(exc)
