#from frictionless import describe
#from frictionless import Resource
import pandas as pd
import json # base python, no pip install needed
import pipe
import os # base python, no pip install needed
import shutil # base python, no pip install needed
import healdata_utils
import pathlib
import jsonschema
from jsonschema import validate
import re
import itertools
from copy import deepcopy

from healdata_utils.schemas import healjsonschema, healcsvschema
from healdata_utils.transforms.frictionless import conversion

from schema_resource_tracker import schema_resource_tracker
from schema_experiment_tracker import schema_experiment_tracker
from schema_results_tracker import schema_results_tracker


def getPositionOfWidgetInLayout(layout,getWidget):
    if layout is not None:
        for i in range(layout.count()):
            print(i)
            row, column, rowSpan, colSpan = layout.getItemPosition(i)
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                if widget == getWidget:
                    #print(i)
                    print(widget)
                    print(widget.text())
                    print("row: ",row,"; column: ", column)
                    return [row,column]

            
def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())

def layoutInLayoutDelete(containerLayout,layoutInLayout):
    for i in range(containerLayout.count()):
        layout_item = containerLayout.itemAt(i)
        if layout_item.layout() == layoutInLayout:
            deleteItemsOfLayout(layout_item.layout())
            containerLayout.removeItem(layout_item)
            break

# def layoutInLayoutDelete(self,containerLayout,layoutInLayout):
#     for i in range(self.containerLayout.count()):
#         layout_item = self.containerLayout.itemAt(i)
#         if layout_item.layout() == layoutInLayout:
#             dsc_pkg_utils.deleteItemsOfLayout(layout_item.layout())
#             self.containerLayout.removeItem(layout_item)
#             break

def get_added_resource_paths(self):
#def get_added_resource_paths():
    
    getDir = self.workingDataPkgDir
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getResourceTrk = os.path.join(getDir,"heal-csv-resource-tracker.csv")
    #getResourcesToAdd = os.path.join(getDir,"resources-to-add.csv")

    if os.path.isfile(getResourceTrk):
        resourceTrackerDf = pd.read_csv(getResourceTrk)
        resourceTrackerDf.fillna("", inplace = True)

        print(resourceTrackerDf)
        print(resourceTrackerDf.columns)

        if "path" in resourceTrackerDf.columns:

            #experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
            resourcePathSeries = resourceTrackerDf["path"].astype(str)
            print(resourcePathSeries,type(resourcePathSeries))
            resourcePathList = resourcePathSeries.tolist()
            print(resourcePathList,type(resourcePathList))
            resourcePathList = [x for x in resourcePathList if x] # remove empty strings
            print(resourcePathList,type(resourcePathList))
            resourcePathList = list(dict.fromkeys(resourcePathList)) # deduplicate list
            print(resourcePathList,type(resourcePathList))

        else: 
            resourcePathList = []

    else:
        resourcePathList = []

    return resourcePathList

def get_resources_to_add(self):
#def get_resources_to_add():
    print("hiiii; getting resource to add file")
    
    getDir = os.path.join(self.workingDataPkgDir,"no-user-access")
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getResourcesToAdd = os.path.join(getDir,"resources-to-add.csv")
    
    # prob need to change to os.path.exists
    if os.path.isfile(getResourcesToAdd):
        resourcesToAddDf = pd.read_csv(getResourcesToAdd)
        resourcesToAddDf.fillna("", inplace = True)
        resourcesToAddDf = resourcesToAddDf[resourcesToAddDf["path"] != ""]
        resourcesToAddDf["date-time"] = pd.to_datetime(resourcesToAddDf["date-time"])

        print(resourcesToAddDf)
        print(resourcesToAddDf.columns)
        print(resourcesToAddDf.shape)

        resourcesToAddDf = resourcesToAddDf[resourcesToAddDf["date-time"] == (resourcesToAddDf.groupby("parent-resource-id")["date-time"].transform("max"))]
        #df[df['date'] < (df.groupby('id')['date'].transform('max') - pd.Timedelta(3, unit='M'))]

        print(resourcesToAddDf)
        print(resourcesToAddDf.columns)
        print(resourcesToAddDf.shape)

    else:
        resourcesToAddDf = None

    return resourcesToAddDf

def get_resources_share_status(self):
    
    #getDir = self.workingDataPkgDir
    getDir = os.path.join(self.workingDataPkgDir,"no-user-access")
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getShareStatus = os.path.join(getDir,"share-status.csv")
    
    # prob need to change to os.path.exists
    if os.path.isfile(getShareStatus):
        shareStatusDf = pd.read_csv(getShareStatus)
        shareStatusDf.fillna("", inplace = True)
        pd.to_datetime(shareStatusDf["date-time"])
        
        print(shareStatusDf)
        print(shareStatusDf.columns)
        print(shareStatusDf.shape)

        # sort by date-time (ascending), then drop duplicates of, keeping the last/latest instance of each path's occurrence
        # to get the latest share status
        shareStatusDf.sort_values(by=["date-time"],ascending=True,inplace=True)
        shareStatusDf.drop_duplicates(subset=["path"],keep="last",inplace=True)
        print("drop duplicates of resource keeping the last/latest instance of each path's occurrence to get the latest share status:")
        print(shareStatusDf.shape)
        
    else:
        shareStatusDf = []

    return shareStatusDf

def get_resources_annotation_mode_status(self):
#def get_resources_annotation_mode_status():
    
    #getDir = self.workingDataPkgDir
    getDir = os.path.join(self.workingDataPkgDir,"no-user-access")
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getAnnotationModeStatus = os.path.join(getDir,"annotation-mode-status.csv")
    
    # prob need to change to os.path.exists
    if os.path.isfile(getAnnotationModeStatus):
        annotationModeStatusDf = pd.read_csv(getAnnotationModeStatus)
        annotationModeStatusDf.fillna("", inplace = True)
        
        print(annotationModeStatusDf)
        print(annotationModeStatusDf.columns)
        print(annotationModeStatusDf.shape)

        # sort by date-time (descending) so that latest annotation mode status value is in first row of df
        annotationModeStatusDf.sort_values(by=["date-time"],ascending=False,inplace=True)
        # get the latest annotation mode status from first row of df as a string
        annotationModeStatus = annotationModeStatusDf["annotation-mode-status"].iloc[0]

    else:
        annotationModeStatus = ""

    return annotationModeStatus

        

    
            

def get_id(self, prefix, fileExt, folderPath):

    if folderPath:

        # get new result ID for new result file - get the max id num used for existing result files and add 1; if no result files yet, set id num to 1
    
        fileList = [filename for filename in os.listdir(folderPath) if filename.startswith(prefix)]
        print(fileList)

        if fileList: # if the list is not empty
            fileStemList = [Path(filename).stem for filename in fileList]
            print(fileStemList)
            #idNumList = [int(filename.rsplit('-',1)[1]) for filename in fileStemList]
            idNumList = [int(filename.split(prefix)[1]) for filename in fileStemList]
            print(resIdNumList)
            idNum = max(idNumList) + 1
            print(max(idNumList),idNum)
        else:
            idNum = 1

        #self.resIdNum = resIdNum
        #self.result_id = 'result-'+ str(self.resIdNum)
        #self.resultFileName = 'result-trk-'+ self.result_id + '.txt'
        fileName = prefix + str(idNum) + fileExt
        #self.saveFilePath = os.path.join(self.saveFolderPath,self.resultFileName)
        saveFilePath = os.path.join(folderPath,fileName)

       

def get_exp_names(self, perResource):
        
    getDir = self.workingDataPkgDir
    getExpTrk = os.path.join(getDir,"heal-csv-experiment-tracker.csv")

    if os.path.isfile(getExpTrk):
        experimentTrackerDf = pd.read_csv(getExpTrk)
        #experimentTrackerDf.replace(np.nan, "")
        experimentTrackerDf.fillna("", inplace = True)

        print(experimentTrackerDf)
        print(experimentTrackerDf.columns)

        if "experimentName" in experimentTrackerDf.columns:

            #experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
            experimentNameSeries = experimentTrackerDf["experimentName"].astype(str)
            print(experimentNameSeries,type(experimentNameSeries))
            
            experimentNameDefaultSeries = pd.Series(["default-experiment-name"])
            
            # add default value to list so that default value is always part of the enum for results and resource tracker experimentNameBelongsTo fields - this allows 
            # default value to be set as the default on drop down for this field 
            experimentNameSeries = pd.concat([experimentNameDefaultSeries,experimentNameSeries], ignore_index=True)
            print(experimentNameSeries,type(experimentNameSeries))
            
            #experimentNameList = experimentTrackerDf["experimentName"].unique().tolist()
            experimentNameList = experimentNameSeries.unique().tolist()
            print(experimentNameList,type(experimentNameList))
            
            experimentNameList[:] = [x for x in experimentNameList if x] # get rid of emtpy strings as empty strings are not wanted and mess up the sort() function
            print(experimentNameList,type(experimentNameList))

            #sortedlist = sorted(list, lambda x: x.rsplit('-', 1)[-1])
            experimentNameList = sorted(experimentNameList, key = lambda x: x.split('-', 1)[0]) # using lambda function to split so can sort on first part of string before a hyphen if a hyphen exists - can't sort on raw strings that include hyphens

            #experimentName = sorted(experimentNameList, lamda x: x.split('-'))
            print(experimentNameList,type(experimentNameList))

            # if ((len(experimentNameList) == 1) and (experimentNameList[0] == "default-experiment-name")):
            #     experimentNameList = []
            #experimentNameList.remove("default-experiment-name")
            #print(experimentNameList,type(experimentNameList))
            
            if perResource:  

                experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
                experimentTrackerDf["experimentId"] = experimentTrackerDf["experimentId"].astype(str)
                
                experimentNameDf = experimentTrackerDf[["experimentId","experimentName"]]
                print(experimentNameDf,type(experimentNameDf))
                
                experimentNameDf.drop_duplicates(inplace=True) 
                experimentNameDf = experimentNameDf[experimentNameDf["experimentName"].str.len() > 0]  

                
            else: 
                experimentNameDf = []


        else:
            print("no experimentName column in experiment tracker")
            experimentNameList = []
            experimentNameDf = []
    else:
        print("no experiment tracker in working data pkg dir")
        # messageText = "<br>Your working Data Package Directory does not contain a properly formatted Experiment Tracker from which to populate unique experiment names for experiments you've already documented. <br><br> The field in this form <b>Experiment Result \"Belongs\" To</b> pulls from this list of experiment names to provide options of study experiments to which you can link your results. Because we cannot populate this list without your experiment tracker, your only option for this field will be the default experiment name: \"default-experiment-name\"." 
        # errorFormat = '<span style="color:red;">{}</span>'
        # self.userMessageBox.append(errorFormat.format(messageText)) 
        experimentNameList = []
        experimentNameDf = []

    print("experimentNameList: ", experimentNameList)
    return experimentNameList, experimentNameDf

def add_exp_names_to_schema(self):


    schemaOrig = self.schema
    experimentNameList = self.experimentNameList

    experimentNameListUpdate = {}
    
    schemaUpdated = deepcopy(schemaOrig)
    enumListOrig = schemaUpdated["properties"]["experimentNameBelongsTo"]["enum"]
    print("enumListOrig: ", enumListOrig)
    #enumListUpdated = enumListOrig.extend(experimentNameList)
    enumListUpdated = experimentNameList
    print("enumListUpdated: ", enumListUpdated)

    schemaUpdated["properties"]["experimentNameBelongsTo"]["enum"] = enumListUpdated
    print("schemaOrig: ",schemaOrig)
    print("schemaUpdated: ", schemaUpdated)

    return schemaUpdated

def getWorkingDataPkgDir(self):

    testPath = self.workingDataPkgDirDisplay.toPlainText()
    print("testPath: ",testPath)

    if not os.path.exists(testPath):
        messageText = "<br>You must set a valid working Data Package Directory to proceed. Navigate to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to either: <br><br>1. <b>Create New Data Package</b>: Create a new Data Package Directory and set it as the working Data Package Directory, or <br>2. <b>Continue Existing Data Package</b>: Set an existing Data Package Directory as the working Data Package Directory."
        errorFormat = '<span style="color:red;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
        return False
    else:
        self.workingDataPkgDir = testPath  
        return True


def heal_metadata_json_schema(metadataType):


    print(metadataType)

    if metadataType == "data-dictionary":
        #schema = healjsonschema["properties"]["data_dictionary"]
        schema = conversion.convert_frictionless_to_jsonschema(healcsvschema)
        

    if metadataType == "resource-tracker":
        schema = schema_resource_tracker
        

    if metadataType == "experiment-tracker":
        schema = schema_experiment_tracker

    if metadataType == "results-tracker":
        schema = schema_results_tracker
        

    if metadataType not in ["data-dictionary","resource-tracker","experiment-tracker","results-tracker"]:
        print("metadata type not supported; metadataType must be one of data-dictionary, resource-tracker, experiment-tracker, results-tracker")
        return
    
    return schema


def heal_metadata_json_schema_properties(metadataType):

    print(metadataType)

    if metadataType == "data-dictionary":
        #props = healjsonschema["properties"]["data_dictionary"]["items"]["properties"]
        intJson = conversion.convert_frictionless_to_jsonschema(healcsvschema)
        props = intJson["items"]["properties"]
        print("csv dd spec props: ", props)
        

    if metadataType == "resource-tracker":
        props = schema_resource_tracker["properties"]
        

    if metadataType == "experiment-tracker":
        props = schema_experiment_tracker["properties"]

    if metadataType == "results-tracker":
        props = schema_results_tracker["properties"]
        

    if metadataType not in ["data-dictionary","resource-tracker","experiment-tracker","results-tracker"]:
        print("metadata type not supported; metadataType must be one of data-dictionary, resource-tracker, experiment-tracker, results-tracker")
        return
    
    return props


def empty_df_from_json_schema_properties(jsonSchemaProperties):
    all_fields = []

    for key, value in jsonSchemaProperties.items():
        p_fullname_list = []
        print(key)
        try:
            p_block = jsonSchemaProperties[key]["properties"]
            p_list = list(p_block.keys())
            p_fullname_list = [key + "." + p for p in p_list]
            print(p_fullname_list)
        except KeyError:
            pass

        if p_fullname_list:
            all_fields.extend(p_fullname_list)
        else:
            all_fields.append(key)

    print(all_fields)
    df = pd.DataFrame(columns = all_fields)    
    return df




def everything_after(df, cols):
    # convenience function to bring one or more cols in a dataframe to the front, while leaving all others in same order following
    # replicates functionality of dplyr 'everything' function - by: https://stackoverflow.com/users/2901002/jezrael
    # cols is a list of col names (list of strings)
    another = df.columns.difference(cols, sort=False).tolist()
    return df[cols + another]

# def get_heal_csv_dd_cols(heal_json_dd_schema_url=None, required_first=True, return_df=False):

#     ###########################################################################
#     # get the latest version of the heal json dd schema to populate the 
#     # heal csv dd template - user can update url in function call if necessary
#     ###########################################################################
    
#     if not heal_json_dd_schema_url:
#         #heal_json_dd_schema_url = 'https://raw.githubusercontent.com/HEAL/heal-metadata-schemas/main/variable-level-metadata-schema/schemas/jsonschema/fields.json'
#          heal_json_dd_schema_url = healdata_utils.schemas.jsonschema_url

#     r = requests.get(heal_json_dd_schema_url)
#     heal_json_dd_schema = r.json()
#     print(heal_json_dd_schema)

#     my_df_col = []

#     for p in list(heal_json_dd_schema['properties'].keys()):
#         if 'properties' in heal_json_dd_schema['properties'][p].keys():
#             for p2 in list(heal_json_dd_schema['properties'][p]['properties'].keys()):
#                 my_df_col.append(p+'.'+p2)
#         else:
#             my_df_col.append(p)
         

#     if not required_first:
#         if not return_df:
#             return my_df_col
#         else:
#             return pd.DataFrame(columns=my_df_col)
#     else: 
#         heal_dd_df = pd.DataFrame(columns=my_df_col)
#         ###########################################################################
#         # get the required fields from the heal json dd schema and put those 
#         # first in the heal csv dd template
#         ###########################################################################

#         required_col = heal_json_dd_schema['required']
#         heal_dd_df = heal_dd_df.pipe(everything_after, required_col)
#         if not return_df:
#             return heal_dd_df.columns.values.tolist()
#         else:
#             return heal_dd_df

def add_dd_to_heal_dd_template(csv_dd_df,required_first=True,save_path=None):
    # csv_dd_df is a csv data dictionary - it can be user-created or come from running infer_dd function on a csv data file
    # if it is user-created, user must ensure that dd column names match those in the heal vlmd field properties
    # e.g. 'name', 'description', 'type', etc. 

    # save path is a string that must end in '.csv'
    
    # get empty df with col names for all the heal vlmd field properties (including 'sub' properties)
    # user can specify whether to put the required properties first but that's the default
    # this is an empty heal csv dd template df
    heal_dd_df = get_heal_csv_dd_cols(required_first=required_first,return_df=True)
    
    # concat the input csv dd to the empty heal csv dd template df to add any info from the user input dd to the 
    # heal template 
    heal_dd_df = pd.concat([heal_dd_df,csv_dd_df])
    
    if save_path:
        heal_dd_df.to_csv(save_path,index=False)

    return heal_dd_df

def new_pkg(pkg_parent_dir_path,pkg_dir_name='dsc-pkg',dsc_pkg_resource_dir_path='./resources/'):
    
    pkg_path = os.path.join(pkg_parent_dir_path,pkg_dir_name)
            
    # create the new package directory    
    try:
        os.makedirs(pkg_path, exist_ok = False)
        print("Directory '%s' created successfully" %pkg_dir_name)
        #os.mkdir(pkg_resources_path) # make the subdir for resources
    except OSError as error:
        print("Directory '%s' can not be created - check to see if the directory already exists")
        return

    
    #destination_folder = pkg_path
    

    for metadataType in ["experiment-tracker", "resource-tracker"]:
        props = heal_metadata_json_schema_properties(metadataType=metadataType)
        df = empty_df_from_json_schema_properties(jsonSchemaProperties=props)

        fName = "heal-csv-" + metadataType + ".csv"
        df.to_csv(os.path.join(pkg_path, fName), index = False) 

    return pkg_path

def new_results_trk():
    
    metadataType = "results-tracker"

    props = heal_metadata_json_schema_properties(metadataType=metadataType)
    df = empty_df_from_json_schema_properties(jsonSchemaProperties=props)

    fName = "heal-csv-" + metadataType + "-(multi-result file to which this result tracker applies).csv"
    #df.to_csv(os.path.join(pkg_path, fName), index = False) 

    return df, fName


def qt_object_properties(qt_object: object) -> dict:
    """
    source: https://stackoverflow.com/questions/50556216/pyqt5-get-list-of-all-properties-in-an-object-qpushbutton
    Create a dictionary of property names and values from a QObject.

    :param qt_object: The QObject to retrieve properties from.
    :type qt_object: object
    :return: Dictionary with format
        {'name': property_name, 'value': property_value}
    :rtype: dict
    """
    properties: list = []

    # Returns a list of QByteArray.
    button_properties: list = qt_object.dynamicPropertyNames()

    for prop in button_properties:
        # Decode the QByteArray into a string.
        name: str = str(prop, 'utf-8')

        # Get the property value from the button.
        value: str = qt_object.property(name)

        properties.append({'name': name, 'value': value})

    return properties

def validateJson(jsonData,jsonSchema):
    # source: https://pynative.com/python-json-validation/
    try:
        validate(instance=jsonData, schema=jsonSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True
    
def get_multi_like_file_descriptions(nameConvention,fileStemList):
    
    allFilesDescribeList = [] 
    messagesOut = []

    nameConventionExplanatoryList = re.findall('{(.+?)}', nameConvention) # list of items enclosed in curly braces
    print(nameConventionExplanatoryList)

    if nameConventionExplanatoryList: # check if user added any naming convention explanatory values in the correct format (between curly braces); if yes, continue, if no, print informative message and return

        nameConventionAllList = re.split('[/{/}]', nameConvention)
        nameConventionAllList = [l for l in nameConventionAllList if l] # list of items delimited by curly braces (either direction)
        print(nameConventionAllList)

        nameOnlyOneExplanatory = False # set default value as false
        # check for delimiters between naming convention explanatory variables - need these to parse filenames to descriptions
        # if length of two lists is same then no delimiters between explanatory values exist, but if list is length one this is handle-able  
        if len(nameConventionAllList) == len(nameConventionExplanatoryList):
            if len(nameConventionAllList) == 1:
                nameOnlyOneExplanatory = True
            else:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                messageText = "Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                #errorFormat = '<span style="color:red;">{}</span>'
                #self.userMessageBox.append(errorFormat.format(messageText))
                messagesOut.append(messageText)
                return allFilesDescribeList, messagesOut

        if not nameOnlyOneExplanatory:
            noDelim = 0
            for idx, l in enumerate(nameConventionAllList):
                beforeVal = None
                afterVal = None
                if l in nameConventionExplanatoryList:
                    if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                        afterVal = nameConventionAllList[idx + 1]
                    if idx != 0: # if not first element, get element before current element  
                        beforeVal = nameConventionAllList[idx - 1]
            
                    if afterVal:
                        if afterVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(l," and ",afterVal," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                            messageText = l," and ",afterVal," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                            messagesOut.append(messageText)
                            #errorFormat = '<span style="color:red;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))
                    if beforeVal:
                        if beforeVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(beforeVal," and ",l," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                            messageText = beforeVal," and ",l," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                            messagesOut.append(messageText)
                            #errorFormat = '<span style="color:red;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))

            if noDelim > 0:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                messageText = "Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                messagesOut.append(messageText)
                #errorFormat = '<span style="color:red;">{}</span>'
                #self.userMessageBox.append(errorFormat.format(messageText))
                return allFilesDescribeList, messagesOut


        allFilesDescribeList = [] 
        
        for i in fileStemList:
            print(i)
        
            oneFileDescribeList = []  

            if nameOnlyOneExplanatory:
                oneFileDescribe = nameConventionAllList[0] + ": " + i
            else: 
                beforeValSave = None
                for idx, l in enumerate(nameConventionAllList):
                    print("idx: ",idx,", l: ",l)
                    beforeVal = None
                    beforeValSplit = None
                    afterVal = None
                    afterValSplit = None
                    if l in nameConventionExplanatoryList:
                        if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                            afterVal = nameConventionAllList[idx + 1]
                            print("afterVal: ",afterVal)
                        if idx != 0: # if not first element, get element first current element  
                            if beforeValSave:
                                beforeVal = beforeValSave + nameConventionAllList[idx - 1]
                                print("YES beforeValSave")
                                print("beforeValSave: ", beforeValSave)
                            else:
                                beforeVal = nameConventionAllList[idx - 1]
                                print("NO beforeValSave")
                            print("beforeVal: ",beforeVal)
                            
            
                        if afterVal:
                            if afterVal in i:
                                afterValSplit = i.split(afterVal)
                                print("afterValSplit: ", afterValSplit)
                        
                            else:
                                #print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",afterVal," as specified by the applied naming convention.")
                                messageText = "the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",afterVal," as specified by the applied naming convention."
                                messagesOut.append(messageText)
                                #errorFormat = '<span style="color:red;">{}</span>'
                                #self.userMessageBox.append(errorFormat.format(messageText))
                                continue

                        if beforeVal:
                            if beforeVal in i:
                                beforeValSplit = i.split(beforeVal)
                                print("beforeValSplit: ", beforeValSplit)
                        
                            else:
                                #print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",beforeVal," as specified by the applied naming convention.")
                                messageText = "the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",beforeVal," as specified by the applied naming convention."
                                messagesOut.append(messageText)
                                #errorFormat = '<span style="color:red;">{}</span>'
                                #self.userMessageBox.append(errorFormat.format(messageText))
                                continue

                        if ((not afterValSplit) and (not beforeValSplit)):
                            #print("the file named ", i, " does not conform to the specified naming convention. It does not contain string(s) specified by the applied naming convention. Exiting check of this file.")
                            messageText = "the file named ", i, " does not conform to the specified naming convention. It does not contain string(s) specified by the applied naming convention. Exiting check of this file."
                            messagesOut.append(messageText)
                            #errorFormat = '<span style="color:red;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))
                            break

                        if ((afterValSplit) and (not beforeValSplit)):
                            myVal = afterValSplit[0]
                            print("afterValSplit ONLY; myVal: ", myVal)

                        if ((not afterValSplit) and (beforeValSplit)):
                            myVal = beforeValSplit[1]
                            print("beforeValSplit ONLY; myVal: ", myVal)
                    
                        if ((afterValSplit) and (beforeValSplit)):
                            #myVal = afterValSplit[0]
                            #print("afterValSplit and beforeValSplit; myVal: ", myVal)
                            #myVal = myVal.split(beforeVal)[1]

                            myVal = beforeValSplit[1]
                            print("afterValSplit and beforeValSplit; myVal 1: ", myVal)
                            myVal = myVal.split(afterVal)[0]
                            print("afterValSplit and beforeValSplit; myVal 2: ", myVal)

                            beforeValSave = beforeVal + myVal
                            print("save beforeValSave: ",beforeValSave)
                    
                        myDescribe = l + ": " + myVal
                        oneFileDescribeList.append(myDescribe)   
            
                oneFileDescribe = ', '.join(oneFileDescribeList)
                print(oneFileDescribe)    
            
            allFilesDescribeList.append(oneFileDescribe) 
            print(allFilesDescribeList) 
    
    return allFilesDescribeList, messagesOut  

    
