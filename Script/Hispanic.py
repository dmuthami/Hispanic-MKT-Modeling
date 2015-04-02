#-------------------------------------------------------------------------------
# Name:        Hispanic Marketing Model Automation
# Purpose:     Based on the automation model
#
# Author:      dmuthami
# Email :      waruid@gmail.com
#
# Created:     01/04/2015(dd/mm/yyyy)
# Copyright:   (c) dmuthami 2015
# Licence:     Absolutely Free for use and distribution
#-------------------------------------------------------------------------------
import os, sys
import logging
import arcpy
import traceback
from arcpy import env
from datetime import datetime

#Set-up logging object
logger = logging.getLogger('hispanic')

def makeSelection(workspace, blockGroup):

    #Apply field delimiters for the Query supplied
    HSP_PercFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "HSP_Perc")
    NHSPBLK_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPBLK_P")
    NHSPAI_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPAI_P")
    NHSPASN_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPASN_P")
    NHSPPI_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPPI_P")
    NHSPWHT_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPWHT_P")
    NHSPOTH_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPOTH_P")
    NHSPMLT_PFieldDelimeter = arcpy.AddFieldDelimiters(env.workspace , "NHSPMLT_P")

    #Expression box query
    #HSP_Perc >= 40 OR (HSP_Perc > NHSPWHT_P AND
    #HSP_Perc > NHSPBLK_P AND HSP_Perc > NHSPAI_P AND
    #HSP_Perc > NHSPASN_P AND HSP_Perc > NHSPPI_P AND
    #HSP_Perc > NHSPOTH_P AND HSP_Perc > NHSPMLT_P)

    # Build the query expression
    SQLExp =  HSP_PercFieldDelimeter + " >= " + "40" + " or ("
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPWHT_PFieldDelimeter + " and "
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPBLK_PFieldDelimeter + " and "
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPAI_PFieldDelimeter + "  and "
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPASN_PFieldDelimeter + " and "
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPPI_PFieldDelimeter + "  and "
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPOTH_PFieldDelimeter + " and "
    SQLExp +=  HSP_PercFieldDelimeter + " > " + NHSPMLT_PFieldDelimeter + " )"

    try:
        # Make a layer from blockgroups feature class
        blockGroupFeatureLayer = blockGroup + '_lyr'

        #delete the in memory feature layer
        # something terrible must have happened since we run the tool and now we have to destroy the
        # the memory imprint of the feature layer
        arcpy.Delete_management(blockGroupFeatureLayer)

    except:
        try:

            #variable pointer to the in-memory feature layer
            blockGroupFeatureLayer = blockGroup + '_lyr'

        except:
            ## Return any Python specific errors and any error returned by the geoprocessor
            ##
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
            msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

            ##Add custom informative message to the Python script tool
            arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
            arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

            ##For debugging purposes only
            ##To be commented on python script scheduling in Windows _log
            print pymsg
            print "\n" +msgs
            logger.info("Forcefully deletes the in memory stores feature layer "+pymsg)
            logger.info("Forcefully deletes the in memory stores feature layer "+msgs)

    #Make feature layer for block group
    arcpy.MakeFeatureLayer_management(blockGroup, blockGroupFeatureLayer)

    #make a fresh selection here
    arcpy.SelectLayerByAttribute_management(blockGroupFeatureLayer, "NEW_SELECTION", SQLExp)


    #Deafult 28748 out of 217486 features from Block groups layer for hispanic as check
    featCount = arcpy.GetCount_management(blockGroupFeatureLayer)
    message = "Number of Hispanic blocks: {0} ".format(featCount)

    #Log message and send to console
    logger.info(message)
    print message

    #Return the feature layer
    return blockGroupFeatureLayer

##Updates hispanic areas based on selection layer and supplied update value
def updateHispanicAreas(workspace,blockGroupFeatureLayer,field,updatevalue):
    try:

        # Start an edit session. Must provide the workspace.
        edit = arcpy.da.Editor(workspace)

        # Edit session is started without an undo/redo stack for versioned data
        #  (for second argument, use False for unversioned data)
        #Compulsory for above feature class participating in a complex data such as parcel fabric
        edit.startEditing(False, False)

        # Start an edit operation
        edit.startOperation()

        #Update cursor goes here
        with arcpy.da.UpdateCursor(blockGroupFeatureLayer, field) as cursor:
            for row in cursor:# loops per record in the recordset and returns an array of objects

                #update zone affiliation to the supplied value
                row[0] = int(updatevalue)

                # Update the cursor with the updated row object that contains now the new record
                cursor.updateRow(row)

        # Stop the edit operation and commit the changes
        edit.stopOperation()

        # Stop the edit session and save the changes
        #Compulsory for release of locks arising from edit session. NB. Singleton principle is observed here
        edit.stopEditing(True)

    except:
            ## Return any Python specific errors and any error returned by the geoprocessor
            ##
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\n updateIPEDSID() Function : Traceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n" +\
                    "Line {0}".format(tb.tb_lineno)
            msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

            ##Add custom informative message to the Python script tool
            arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
            arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

            ##For debugging purposes only
            ##To be commented on python script scheduling in Windows _log
            print pymsg
            print "\n" +msgs
            logger.info( pymsg)
            logger.info(msgs)

    return ""

##Calculate race percentage
def calculateRacePercentage(workspace,blockGroupFeatureLayer,fieldsPer,fieldsPop):
    try:

        # Start an edit session. Must provide the workspace.
        edit = arcpy.da.Editor(workspace)

        # Edit session is started without an undo/redo stack for versioned data
        #  (for second argument, use False for unversioned data)
        #Compulsory for above feature class participating in a complex data such as parcel fabric
        edit.startEditing(False, False)

        # Start an edit operation
        edit.startOperation()

        #merge the list of the fields
        mergedFieldList =fieldsPer + fieldsPop

        #Update cursor goes here
        with arcpy.da.UpdateCursor(blockGroupFeatureLayer, mergedFieldList) as cursor:
            for row in cursor:# loops per record in the recordset and returns an array of objects

                ##Sample lists of the fields
                #fieldsPer = ["HSP_Perc","NHSPWHT_P","NHSPBLK_P","NHSPAI_P","NHSPASN_P","NHSPPI_P","NHSPOTH_P","NHSPMLT_P"]
                #fieldsPop = ["HISPPOP_CY","NHSPWHT_CY","NHSPBLK_CY","NHSPAI_CY","NHSPASN_CY","NHSPPI_CY","NHSPOTH_CY","NHSPMLT_CY","TOTPOP_CY"]

                #Compute percentage for each group

                totalPopulation = row[mergedFieldList.index("TOTPOP_CY")]
                row[mergedFieldList.index("HSP_Perc")] = int((float(row[mergedFieldList.index("HISPPOP_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPWHT_P")] = int((float(row[mergedFieldList.index("NHSPWHT_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPBLK_P")] = int((float(row[mergedFieldList.index("NHSPBLK_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPAI_P")] = int((float(row[mergedFieldList.index("NHSPAI_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPASN_P")] = int((float(row[mergedFieldList.index("NHSPASN_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPPI_P")] = int((float(row[mergedFieldList.index("NHSPPI_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPOTH_P")] = int((float(row[mergedFieldList.index("NHSPOTH_CY")])*100.0)/float(totalPopulation))
                row[mergedFieldList.index("NHSPMLT_P")] = int((float(row[mergedFieldList.index("NHSPMLT_CY")])*100.0)/float(totalPopulation))

                # Update the cursor with the updated row object that contains now the new record
                cursor.updateRow(row)

        # Stop the edit operation.and commit the changes
        edit.stopOperation()

        # Stop the edit session and save the changes
        #Compulsory for release of locks arising from edit session. NB. Singleton principle is observed here
        edit.stopEditing(True)

        #delete the in memory feature layer just in case we need to recreate
        # feature layer or maybe run script an additional time
        arcpy.Delete_management(blockGroupFeatureLayer)

    except:
            ## Return any Python specific errors and any error returned by the geoprocessor
            ##
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\n updateIPEDSID() Function : Traceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n" +\
                    "Line {0}".format(tb.tb_lineno)
            msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

            ##Add custom informative message to the Python script tool
            arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
            arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

            ##For debugging purposes only
            ##To be commented on python script scheduling in Windows _log
            print pymsg
            print "\n" +msgs
            logger.info( pymsg)
            logger.info(msgs)

    return ""

#main function
def ulimsPerfomanceManagement():
    try:
        #Timestamp appended t the log file#
        currentDate = datetime.now().strftime("-%d-%m-%y_%H-%M-%S") # Current time

        #Set-up some error logging code.
        logfile = r"C:\DAVID-MUTHAMI\GIS Data\RED-BULL\Hispanic Market Potential\Hispanic MKT Modeling\Script" + "\\"+ "hispanic_logfile" + str(currentDate)+ ".log"

        hdlr = logging.FileHandler(logfile)#file handler
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')# formatter object
        hdlr.setFormatter(formatter)#link handler and formatter object
        logger.addHandler(hdlr)# add handler to the logger object
        logger.setLevel(logging.INFO)#Set the logging level

        #Workspace
        _workspace = r"C:\DAVID-MUTHAMI\GIS Data\RED-BULL\Hispanic Market Potential\Hispanic MKT Modeling\Demo.gdb"
        env.workspace = _workspace

        ## Set overwrite in workspace to true
        env.overwriteOutput = True

        #Feature class used in system
        blockGroup = "BG_Demo"
        stores = "US_Stores"

        #Make selection where total population is greater than 0
                    #collegiate definition
        totalPopulationFieldwithDelimeter = arcpy.AddFieldDelimiters(env.workspace , \
            "TOTPOP_CY")

        # Select  Total population greater than 0
        totalPopulationSQLExp =  totalPopulationFieldwithDelimeter + " > " + "0"

        try:
            # Make a layer from blockgroups feature class
            blockGroupFeatureLayer = blockGroup + '_lyr'

            #delete the in memory feature layer
            # something terrible must have happened since we run the tool and now we have to destroy the
            # the memory imprint of the feature layer
            arcpy.Delete_management(blockGroupFeatureLayer)

        except:
            try:

                #variable pointer to the in-memory feature layer
                blockGroupFeatureLayer = blockGroup + '_lyr'

            except:
                ## Return any Python specific errors and any error returned by the geoprocessor
                ##
                tb = sys.exc_info()[2]
                tbinfo = traceback.format_tb(tb)[0]
                pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                        str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
                msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

                ##Add custom informative message to the Python script tool
                arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
                arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

                ##For debugging purposes only
                ##To be commented on python script scheduling in Windows _log
                print pymsg
                print "\n" +msgs
                logger.info("Forcefully deletes the in memory stores feature layer "+pymsg)
                logger.info("Forcefully deletes the in memory stores feature layer "+msgs)

        #Make feature layer for block group
        arcpy.MakeFeatureLayer_management(blockGroup, blockGroupFeatureLayer)

        #make a fresh selection here
        arcpy.SelectLayerByAttribute_management(blockGroupFeatureLayer, "NEW_SELECTION", totalPopulationSQLExp)

        #Fields array
        fieldsPer = ["HSP_Perc","NHSPWHT_P","NHSPBLK_P","NHSPAI_P","NHSPASN_P","NHSPPI_P","NHSPOTH_P","NHSPMLT_P"]
        fieldsPop = ["HISPPOP_CY","NHSPWHT_CY","NHSPBLK_CY","NHSPAI_CY","NHSPASN_CY","NHSPPI_CY","NHSPOTH_CY","NHSPMLT_CY","TOTPOP_CY"]

        ##Call function to compute percentages
        calculateRacePercentage(env.workspace,blockGroupFeatureLayer,fieldsPer,fieldsPop)

        #Make selection of hispanic layer and return feature layer
        blockGroupFeatureLayer = makeSelection(env.workspace, blockGroup)

        field = ["zone_affiliation"]#he field stores if block group is hispanic or not
        updatevalue = 1 #update domain value for hispanic
        #For hispanic layer. Call function & Persist to value 1
        updateHispanicAreas(env.workspace,blockGroupFeatureLayer,field,updatevalue)

        #Switch selection to non hispanic
        arcpy.SelectLayerByAttribute_management(blockGroupFeatureLayer, "SWITCH_SELECTION")
        updatevalue = 0 #set update value for non-hispanic layer

        # Default check =217486-28748 non-hispanic blocks from Block groups layer
        featCount = arcpy.GetCount_management(blockGroupFeatureLayer)
        message = "Number of Non-Hispanic blocks: {0} ".format(featCount)

        #For hispanic layer. Persist to value 0
        updateHispanicAreas(env.workspace,blockGroupFeatureLayer,field,updatevalue)

        #Switch selection to Hispanic
        arcpy.SelectLayerByAttribute_management(blockGroupFeatureLayer, "SWITCH_SELECTION")

        #Make feature layer for stores
        storesFeatureLayer = stores + "_Lyr"

        #Make feature layer for stores feature class
        arcpy.MakeFeatureLayer_management(stores, storesFeatureLayer)

        #Select by location only those stores falling under Hispanic
        arcpy.SelectLayerByLocation_management(storesFeatureLayer, 'intersect', blockGroupFeatureLayer, "","NEW_SELECTION")

        # Persist selected stores features to a new featureclass
        arcpy.CopyFeatures_management(storesFeatureLayer, "stores_hispanic")

        #Attempt to delete block group feature layer
        try:
            #delete the in memory feature layer
            # something terrible must have happened since we run the tool and now we have to destroy the
            # the memory imprint of the feature layer
            arcpy.Delete_management(blockGroupFeatureLayer)

        except:

            ## Return any Python specific errors and any error returned by the geoprocessor
            ##
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
            msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

            ##Add custom informative message to the Python script tool
            arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
            arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

            ##For debugging purposes only
            ##To be commented on python script scheduling in Windows _log
            print pymsg
            print "\n" +msgs
            logger.info("Forcefully deletes the in memory stores feature layer "+pymsg)

        #Attempt to delete stores feature layer
        try:
            #delete the in memory feature layer
            # something terrible must have happened since we run the tool and now we have to destroy the
            # the memory imprint of the feature layer
            arcpy.Delete_management(storesFeatureLayer)

        except:

            ## Return any Python specific errors and any error returned by the geoprocessor
            ##
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
            msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

            ##Add custom informative message to the Python script tool
            arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
            arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

            ##For debugging purposes only
            ##To be commented on python script scheduling in Windows _log
            print pymsg
            print "\n" +msgs
            logger.info("Forcefully deletes the in memory stores feature layer "+pymsg)

        #On success perfomace tuning complete is written to a variable
        msg = "Hispanic Tool Automation Succeeded"
        #Write to console
        print msg
        #Write to log file
        logger.info(msg)

    except:
        ## Return any Python specific errors and any error returned by the geoprocessor
        ##
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\n ulimsPerfomanceManagement() Function : Traceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n" +\
                "Line {0}".format(tb.tb_lineno)
        msgs = "Geoprocessing  Errors :\n" + arcpy.GetMessages(2) + "\n"

        ##Add custom informative message to the Python script tool
        arcpy.AddError(pymsg) #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).
        arcpy.AddError(msgs)  #Add error message to the Python script tool(Progress dialog box, Results windows and Python Window).

        ##For debugging purposes only
        ##To be commented on python script scheduling in Windows _log
        print pymsg
        logger.info(pymsg)
        print "\n" +msgs
        logger.info(msgs)

def main():
    pass

if __name__ == '__main__':
    main()
    #Run perfomance management module
    ulimsPerfomanceManagement()
