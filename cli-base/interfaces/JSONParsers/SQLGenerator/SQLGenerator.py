#!/usr/bin/python
__author__ = 'ender_al'
import json
import sys,getopt
import lib.db_conn as DBConn
import MySQLdb

monitored_systems = []
pep = []
mitigation_actions = []
detrimental_events = []


database_connection = DBConn.DBConn()

sql_file = ""

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def validateInputJSON(uri):
    try:
        json_file = open(uri)
        js = json.load(json_file)
        print "Valid JSON File"
    except ValueError, e:
        return False

    return js

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def traverseAuthorizedMAJSON(jsonInstance):
    print "-------------------------------------------------------------------------"
    print "Monitored System ID: ",jsonInstance["monitored_System_Ident"]
    print "There are '",len(jsonInstance["mitigationAction"]),"' mitigation action in this JSON instance."

    ma_cou = 1
    for ma in jsonInstance["mitigationAction"]:
        print "-------------------------------------------------------------------------"
        print "Information of Mitigation Action: ", ma_cou
        traverse_nodes(ma, "mitigationAction")
        ma_cou += 1

    return

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getLastAutoIncrementedID(tableName):

    #Check if RORI_DB is created
    query = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'RORI_DB';"
    try:
        result = database_connection.execute(query)
    except MySQLdb.Error, e:
        try:
            error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            return 1, error
        except IndexError:
            error = "MySQL Error: %s" % str(e)
            return 1, error

    # Check the result returned by MySQL
    try:
        db_name = result[0][0]
        if db_name != "RORI_DB":
            return 1, "Error: RORI database is not created!!!"
    except IndexError:
        return 1, "Error: RORI database is not created!!!"


    #Check if Table exits:
    query = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'RORI_DB' AND TABLE_NAME = %s";
    values = (tableName)
    try:
        result = database_connection.execute(query, values)
    except MySQLdb.Error, e:
        try:
            error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            print error
            return 1, error
        except IndexError:
            error = "MySQL Error: %s" % str(e)
            print error
            return 1, error

    # Check the result returned by MySQL
    try:
        table_count = result[0][0]
        if table_count == 0:
            return 1, "Error: Table "+tableName+" doesn't exists!!"
    except IndexError:
        return 1, "Error: Table "+tableName+" doesn't exists!!"

    #Select the Last ID count
    query = "SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'RORI_DB' AND TABLE_NAME = %s";
    values = (tableName)
    try:
        result = database_connection.execute(query, values)
    except MySQLdb.Error, e:
        try:
            error = "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            print error
            return 1, error
        except IndexError:
            error = "MySQL Error: %s" % str(e)
            print error
            return 1, error

    # Check the result returned by MySQL
    try:
        result = result[0][0]
    except IndexError:
        return 1, "Error: There is not AUTO_INCREMENT Value in table "+tableName+"!!"

    return 0, result

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getOrganization(jsonInstance, sql_file):

    #Get last ID inserted in the table Organization
    ok, org_lastID = getLastAutoIncrementedID('Organization')
    if ok == 0:
        #org_lastID = org_lastID[0][0]
        org_name = jsonInstance['monitored_System_Ident']

        if org_name == "":
            print "Error: No info Related to Organization in XOrBAC file"
            sys.exit(2)

        monitored_systems.append({"id":org_lastID,"name":org_name,"description":''})
        insert_query = ("INSERT INTO `Organization` VALUES ({0},'{1}','{2}');".format(org_lastID,org_name,''))

        #Write to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- Organization Table Data\n")
            myfile.write("LOCK TABLES `Organization` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `Organization` DISABLE KEYS */;\n")
            myfile.write(insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `Organization` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

    else:
        print org_lastID
        sys.exit(2)
    return


#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getEquipments(jsonInstance, sql_file):

    #Get last ID inserted in the table Equipment and AEV
    equ_ok, equ_lastID = getLastAutoIncrementedID('Equipment')
    aev_ok, aev_lastID = getLastAutoIncrementedID('AEV')
    if equ_ok == 0 and aev_ok == 0:
        equ_values = []
        aev_values = []
        org_id = None

        for org in monitored_systems:
            if jsonInstance['monitored_System_Ident'] == org["name"]:
                org_id = org["id"]

        if org_id == None:
            print "Error: The information of Equipments in this XOrBAC instance is not related to any known Organization"
            sys.exit(2)

        for equ in jsonInstance['policy_enforcement_point']:
            equ_values.append("({0},'{1}','{2}','{3}')".format(equ_lastID,equ["id"],equ["name"],equ["type"]))
            pep.append({"id":equ_lastID,"idRef":equ["id"]})

            if "AEV" in equ:
                aev_values.append("({0},{1},{2},{3},{4},{5},{6},{7},{8},{9})".format(aev_lastID,0.00,0.00,0.00,0.00,0.00,1,equ["AEV"],org_id,equ_lastID))
                aev_lastID +=1
            equ_lastID += 1

        if len(equ_values) == 0:
            print "Error: No info Related to Equipments in XOrBAC file"
            sys.exit(2)

        equ_insert_query = "INSERT INTO `Equipment` VALUES "+(",").join(equ_values)+";"

        #Write Equipments to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- Equipment Table Data\n")
            myfile.write("LOCK TABLES `Equipment` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `Equipment` DISABLE KEYS */;\n")
            myfile.write(equ_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `Equipment` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

        if len(aev_values) == 0:
            print "Error: No info Related to AEV in XOrBAC file"
            sys.exit(2)

        aev_insert_query = "INSERT INTO `AEV` VALUES "+(",").join(aev_values)+";"

        #Write AEV to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- AEV Table Data\n")
            myfile.write("LOCK TABLES `AEV` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `AEV` DISABLE KEYS */;\n")
            myfile.write(aev_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `AEV` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

    else:
        print equ_lastID
        print aev_lastID
        sys.exit(2)
    return


#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getMitigationActions(jsonInstance, sql_file):

    #Get last ID inserted in the table Countermeasure and ARC
    ma_ok, ma_lastID = getLastAutoIncrementedID('Countermeasure')
    arc_ok, arc_lastID = getLastAutoIncrementedID('ARC')
    if ma_ok == 0 and arc_ok == 0:
        ma_values = []
        arc_values = []
        org_id = None

        for org in monitored_systems:
            if jsonInstance['monitored_System_Ident'] == org["name"]:
                org_id = org["id"]

        if org_id == None:
            print "Error: The information of Authorized Mitigation Actions in this JSON instance is not related to any known Organization"
            sys.exit(2)

        for ma in jsonInstance['mitigationAction']:

            for eq in pep:
                if eq["idRef"] == ma["enforcementPoints"][0]["ident"]:
                    ma_eq = eq["id"]
                    break

            ma_values.append("({0},'{1}','{2}','{3}',{4},{5})".format(ma_lastID,ma["mitigationAction_Ident"],ma["name"].replace("'","\\'"),ma["description"].replace("'","\\'"),0,ma_eq))
            mitigation_actions.append({"id":ma_lastID,"idRef":ma["mitigationAction_Ident"]})

            if "annualResponseCost" in ma:
                arc_total = ma["annualResponseCost"]["totalCost"]
                arc_values.append("({0},{1},{2},{3},{4},{5},{6})".format(arc_lastID,0.00,0.00,0.00,0.00,arc_total,ma_lastID))
                arc_lastID +=1
            ma_lastID += 1

        if len(ma_values) == 0:
            print "Error: No info Related to Mitigation Actions in this JSON file"
            sys.exit(2)

        ma_insert_query = "INSERT INTO `Countermeasure` VALUES "+(",").join(ma_values)+";"

        #Write Equipments to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- Countermeasure Table Data\n")
            myfile.write("LOCK TABLES `Countermeasure` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `Countermeasure` DISABLE KEYS */;\n")
            myfile.write(ma_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `Countermeasure` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

        if len(arc_values) == 0:
            print "Error: No info Related to ARC in this JSON file"
            sys.exit(2)

        arc_insert_query = "INSERT INTO `ARC` VALUES "+(",").join(arc_values)+";"

        #Write AEV to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- ARC Table Data\n")
            myfile.write("LOCK TABLES `ARC` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `ARC` DISABLE KEYS */;\n")
            myfile.write(arc_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `ARC` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

    else:
        print ma_lastID
        print arc_lastID
        sys.exit(2)

    return

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getDetrimentalEvents(jsonInstance, sql_file):

    #Get last ID inserted in the table Incident
    de_ok, de_lastID = getLastAutoIncrementedID('Incident')

    if de_ok == 0:
        de_values = []
        org_id = None

        for org in monitored_systems:
            if jsonInstance['monitored_System_Ident'] == org["name"]:
                org_id = org["id"]

        if org_id == None:
            print "Error: The information of Detrimental Events in this JSON instance is not related to any known Organization"
            sys.exit(2)

        for de in jsonInstance['detrimentalEvent']:
            if de["proactiveElementaryRisk"][0]["impact"] == "high":
                risk_level = "H"
            elif de["proactiveElementaryRisk"][0]["impact"] == "medium":
                risk_level = "M"
            elif de["proactiveElementaryRisk"][0]["impact"] == "low":
                risk_level = "L"
            de_values.append("({0},'{1}','{2}','{3}','{4}')".format(de_lastID,de["ident"],de["name"].replace("'","\\'"),de["description"].replace("'","\\'"),risk_level))

            detrimental_events.append({"id":de_lastID,"idRef":de["ident"]})

            de_lastID += 1

        if len(de_values) == 0:
            print "Error: No info Related to Detrimental Events in this JSON file"
            sys.exit(2)

        de_insert_query = "INSERT INTO `Incident` VALUES "+(",").join(de_values)+";"

        #Write Equipments to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- Incident Table Data\n")
            myfile.write("LOCK TABLES `Incident` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `Incident` DISABLE KEYS */;\n")
            myfile.write(de_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `Incident` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

    else:
        print de_lastID
        sys.exit(2)
    return

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getDetrimentalEventMitigationAction(jsonInstance, sql_file):

    dema_values = []
    org_id = None

    for org in monitored_systems:
        if jsonInstance['monitored_System_Ident'] == org["name"]:
            org_id = org["id"]

    if org_id == None:
        print "Error: The information of the association of Incidents and Countermeasures in this XOrBAC file is not related to any known Organization"
        sys.exit(2)

    for dema_item in jsonInstance['detrimental_event_mitigation_action']:
        de_id = None

        for de in detrimental_events:
            if de["idRef"] == dema_item["detrimental_event_id"]:
                de_id = de["id"]
                break

        for ma in mitigation_actions:
            if ma["idRef"] in dema_item["mitigation_actions_id"]:
                dema_values.append("({0},{1})".format(de_id,ma["id"]))

    if len(dema_values) == 0:
        print "Error: No information of the association of Incidents and Countermeasures in XOrBAC file"
        sys.exit(2)

    equ_insert_query = "INSERT INTO `Incident_has_Countermeasure` VALUES "+(",").join(dema_values)+";"

    #Write Equipments to File
    with open(sql_file, 'a') as myfile:
        myfile.write("\n\n-- Incident_has_Countermeasure Table Data\n")
        myfile.write("LOCK TABLES `Incident_has_Countermeasure` WRITE;\n")
        myfile.write("/*!40000 ALTER TABLE `Incident_has_Countermeasure` DISABLE KEYS */;\n")
        myfile.write(equ_insert_query+"\n")
        myfile.write("/*!40000 ALTER TABLE `Incident_has_Countermeasure` ENABLE KEYS */;\n")
        myfile.write("UNLOCK TABLES;\n")
    myfile.closed

    return

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getRiskMitigation(jsonInstance, sql_file):

    #Get last ID inserted in the table RM
    rm_ok, rm_lastID = getLastAutoIncrementedID('RM')

    if rm_ok == 0:
        rm_values = []
        org_id = None

        for org in monitored_systems:
            if jsonInstance['monitored_System_Ident'] == org["name"]:
                org_id = org["id"]

        if org_id == None:
            print "Error: The information of Risk Mitigation in this XOrBAC file is not related to any known Organization"
            sys.exit(2)

        for rm in jsonInstance['mitigation_action_risk_mitigation']:
            for ma in mitigation_actions:
                if ma["idRef"] == rm["mitigation_action"]:
                    ma_id = ma["id"]
                    break

            rm_values.append("({0},{1},{2},{3},{4})".format(rm_lastID,rm["EF"],rm["COV"],rm["RM"],ma_id))

            rm_lastID += 1

        if len(rm_values) == 0:
            print "Error: No info Related to Risk Mitigation in this JSON file"
            sys.exit(2)

        rm_insert_query = "INSERT INTO `RM` VALUES "+(",").join(rm_values)+";"

        #Write Equipments to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- RM Table Data\n")
            myfile.write("LOCK TABLES `RM` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `RM` DISABLE KEYS */;\n")
            myfile.write(rm_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `RM` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

    else:
        print rm_lastID
        sys.exit(2)
    return

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def getDetrimentalEventALE(jsonInstance, sql_file):

    #Get last ID inserted in the table ALE
    ale_ok, ale_lastID = getLastAutoIncrementedID('ALE')

    if ale_ok == 0:
        ale_values = []
        org_id = None

        for org in monitored_systems:
            if jsonInstance['monitored_System_Ident'] == org["name"]:
                org_id = org["id"]

        if org_id == None:
            print "Error: The information of ALE in this XOrBAC file is not related to any known Organization"
            sys.exit(2)

        for ale in jsonInstance['detrimental_event_ale']:
            for de in detrimental_events:
                if de["idRef"] == ale["detrimental_event_id"]:
                    de_id = de["id"]
                    break
            ale_values.append("({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12})".format(ale_lastID,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,1,ale["ale"],de_id,org_id))

            ale_lastID += 1

        if len(ale_values) == 0:
            print "Error: No info related to ALE in this JSON file"
            sys.exit(2)

        rm_insert_query = "INSERT INTO `ALE` VALUES "+(",").join(ale_values)+";"

        #Write ALE to File
        with open(sql_file, 'a') as myfile:
            myfile.write("\n\n-- ALE Table Data\n")
            myfile.write("LOCK TABLES `ALE` WRITE;\n")
            myfile.write("/*!40000 ALTER TABLE `ALE` DISABLE KEYS */;\n")
            myfile.write(rm_insert_query+"\n")
            myfile.write("/*!40000 ALTER TABLE `ALE` ENABLE KEYS */;\n")
            myfile.write("UNLOCK TABLES;\n")
        myfile.closed

    else:
        print ale_lastID
        sys.exit(2)
    return
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def main(argv):
    sql_file = './mydump.sql'
    xorbacInstanceURI = ''
    mitigationActionInstanceURI = ''
    riskProfileInstanceURI = ''

    try:
        opts, args = getopt.getopt(argv,"h",["xorbac=","ma=","rp=","outsql="])
    except getopt.GetoptError:
        print 'Usage: '
        print 'sqlGenerator.py --xorbac <inputXOrBAC> --ma <inputMitigationActions> --rp <inputRiskProfile> --outsql <NameOfSQLOutput>'
        sys.exit(2)

    if not opts:
        print 'Usage: '
        print 'sqlGenerator.py --xorbac <inputXOrBAC> --ma <inputMitigationActions> --rp <inputRiskProfile> --outsql <NameOfSQLOutput>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'Usage: '
            print 'sqlGenerator.py --xorbac <inputXOrBAC> --ma <inputMitigationActions> --rp <inputRiskProfile> --outsql <NameOfSQLOutput>'
            sys.exit()
        elif opt in ("--xorbac"):
            xorbacInstanceURI = arg
        elif opt in ("--ma"):
            mitigationActionInstanceURI = arg
        elif opt in ("--rp"):
            riskProfileInstanceURI = arg
        elif opt in ("--outsql"):
            sql_file = arg


    #Check XOrBAC file
    if xorbacInstanceURI != "":
        xorbacJSONInstance = validateInputJSON(xorbacInstanceURI)
        if xorbacJSONInstance == False:
            print "Error: The JSON file provided has a bad syntax!!!"
            sys.exit(2)
    else:
        print "Error: XOrBAC file should be provided!!!!"
        sys.exit(2)

    #Check Mitigation Actions JSON
    if mitigationActionInstanceURI !="":
        mitigationActionJSONInstance = validateInputJSON(mitigationActionInstanceURI)
        if mitigationActionJSONInstance == False:
            print "The Authorized Mitigation Actions JSON file provided has a bad syntax!!!"
            sys.exit(2)
    else:
        print "Error: Authorized Mitigation Actions JSON file should be provided!!!!"
        sys.exit(2)

    #Check Risk Profile JSON
    if riskProfileInstanceURI !="":
        riskProfileJSONInstance = validateInputJSON(riskProfileInstanceURI)
        if riskProfileJSONInstance == False:
            print "The Risk Profile JSON file provided has a bad syntax!!!"
            sys.exit(2)
    else:
        print "Error: Risk Profile JSON file should be provided!!!!"
        sys.exit(2)

    #--------------------------------------------------------------------------------------------------------------------
    #Print headers of Dump SQL file
    with open(sql_file, 'w') as myfile:
        myfile.write("-- RFIA Database Population\n")
        myfile.write("/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;\n")
        myfile.write("/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;\n")
        myfile.write("/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;\n")
        myfile.write("/*!40101 SET NAMES utf8 */;\n")
        myfile.write("/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;\n")
        myfile.write("/*!40103 SET TIME_ZONE='+00:00' */;\n")
        myfile.write("/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;\n")
        myfile.write("/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;\n")
        myfile.write("/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;\n")
        myfile.write("/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;\n")
    myfile.closed




    # Generate SQL queries for Organization from XOrBAC file
    print "Get Organizations from XOrBAC file"
    getOrganization(xorbacJSONInstance,sql_file)
    print "Get PEP info from XOrBAC file"
    getEquipments(xorbacJSONInstance,sql_file)

    # Generate SQL queries from Mitigation Action file
    print "Get Mitigation Action from AuthorizedMitigation JSON file"
    getMitigationActions(mitigationActionJSONInstance,sql_file)
    # Generate SQL queries from Risk Profile file
    print "Get Detrimental Event from RiskProfile JSON file"
    getDetrimentalEvents(riskProfileJSONInstance,sql_file)

    # Generate SQL queries for Organization from XOrBAC file to establish relations among Incident-Countermeasures
    # RiskMitigation - Countermeasures, Incidents - ALE
    print "Get relations between Detrimental Events and Mitigation Actions from XOrBAC file"
    getDetrimentalEventMitigationAction(xorbacJSONInstance,sql_file)
    print "Get relations between Risk Mitigation and Mitigation Actions from XOrBAC file"
    getRiskMitigation(xorbacJSONInstance,sql_file)
    print "Get relations between ALE, Detrimental Events and Organizations from XOrBAC file"
    getDetrimentalEventALE(xorbacJSONInstance,sql_file)


    #--------------------------------------------------------------------------------------------------------------------
    #Print footer of Dump SQL file
    with open(sql_file, 'a') as myfile:
        myfile.write("/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;\n")
        myfile.write("/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;\n")
        myfile.write("/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;\n")
        myfile.write("/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;\n")
        myfile.write("/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;\n")
        myfile.write("/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;\n")
        myfile.write("/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;\n")
        myfile.write("/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;\n")
    myfile.closed

    print ">>> SQL File Generated and Save in: ",sql_file
if __name__ == "__main__":
    main(sys.argv[1:])

