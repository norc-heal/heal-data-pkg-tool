# importing the shutil module
import shutil
 
# importing the os module
import os

import pathlib
from pathlib import Path

import dsc_pkg_utils
import pandas as pd
import ast



# defining the function to ignore the files 
# if present in any folder that does not start with "dsc-pkg"
# when folder starts with dsc-pkg do NOT ignore the files for copying
def ignore_files_1(dir, files):
    
    dirStem = Path(dir)
    dirStem = dirStem.stem
    dirStemString = str(dirStem)

    if not dirStemString.startswith("dsc-pkg"): # in this case subfolders in dsc pkg will not have files copied over
    #if not "dsc-pkg" in dir: # in this case subfolders in dsc pkg should have files copied over
        return [f for f in files if os.path.isfile(os.path.join(dir, f))]
    else:
        return []

# # defining the function to ignore the files 
# # if present in any folder that does not start with "dsc-pkg"
# # when folder starts with dsc-pkg do NOT ignore the files for copying
# def ignore_files_2(dir, files, filesToKeep=[]):
    
#     dirStem = Path(dir)
#     dirStem = dirStem.stem
#     dirStemString = str(dirStem)

#     #if not dirStemString.startswith("dsc-pkg"): # in this case subfolders in dsc pkg will not have files copied over
#     if not "dsc-pkg" in dir: # in this case subfolders in dsc pkg should have files copied over
#         filesToIgnore = [f for f in files if os.path.isfile(os.path.join(dir, f))]
#         filesToIgnore = [f for f in filesToIgnore if os.path.join(dir, f) not in filesToKeep]
#         return filesToIgnore
#     else:
#         return []

# defining the function to ignore the files 
# if present in any folder that does not start with "dsc-pkg"
# when folder starts with dsc-pkg do NOT ignore the files for copying
def ignore_files_2(filesToKeep):
    def ignoref(dir, files):
    
        dirStem = Path(dir)
        dirStem = dirStem.stem
        dirStemString = str(dirStem)

        if not dirStemString.startswith("dsc-pkg"): # in this case subfolders in dsc pkg will not have files copied over
        #if not "dsc-pkg" in dir: # in this case subfolders in dsc pkg should have files copied over
            filesToIgnore = [f for f in files if os.path.isfile(os.path.join(dir, f))]
            #filesToIgnore = set(filesToIgnore) - set(filesToKeep)
            filesToIgnore = [f for f in filesToIgnore if Path(os.path.join(dir, f)) not in filesToKeep]
            print("dir: ", dir)
            print("filesToIgnore: ", filesToIgnore)
            return filesToIgnore
        else:
            print("dir: ", dir)
            #filesToIgnore = [f for f in os.listdir(dir) if f.endswith(".txt")]
            filesToIgnore = [f for f in files if os.path.isfile(os.path.join(dir, f))]
            filesToIgnore = [f for f in filesToIgnore if Path(os.path.join(dir, f)) not in filesToKeep]
            filesToIgnore.extend(["archive","no-user-access"])
            print("filesToIgnore: ", filesToIgnore)
            return filesToIgnore
    return ignoref

def createShareableDataPkg(workingDataPkgDir,flavor="shell",byDate="1/1/2099",shareableDataPkgShellDir="",StudyFolderCentralized=True,workingDataPkgDirInStudyFolder=True):
    # calling the shutil.copytree() method and
    # passing the src,dst,and ignore parameter
    workingDataPkgDirPath = Path(workingDataPkgDir)
    workingDataPkgDirStem = workingDataPkgDirPath.stem
    workingDataPkgDirParentPath = workingDataPkgDirPath.parent

    if StudyFolderCentralized:
        if workingDataPkgDirInStudyFolder:
            if not shareableDataPkgShellDir:
                studyFolderDirPath = workingDataPkgDirParentPath # working data pkg dir is direct subdir of study folder, so study folder is parent of working data pkg dir
                studyFolderDirParentPath = studyFolderDirPath.parent # get parent of study dir because this is where we will want to put the shareable data pkg shell and shareable data pkg(s)
                studyFolderDirParentString = str(studyFolderDirParentPath)
                
                studyFolderDirStemString = str(studyFolderDirPath.stem)
                
                # create a folder at the same level as study folder called my-study-shareable-data-pkgs
                # this folder will contain the timestamped shareable data pkg shell and any created shareable data pkg(s), also timestamped
                # this means that every time you want to share - you will have a new timestamped shareable shell and shareable data pkg(s)
                # this will allow you to always find a previously shared version and to always know which was the latest shared version
                shareableDirStemString = studyFolderDirStemString + "-shareable-data-pkgs" + "-" + pd.Timestamp("now").strftime('%Y-%m-%d')
                shareableDirString = os.path.join(studyFolderDirParentString,shareableDirStemString)
                if not os.path.exists(shareableDirString):
                    os.mkdir(shareableDirString)

                if "by-date" in flavor:
                    shareablePkgDirStemString = studyFolderDirStemString + "-shareable-data-pkg-" + flavor + "-" + pd.Timestamp(byDate).strftime('%Y-%m-%d') 
                else:
                    shareablePkgDirStemString = studyFolderDirStemString + "-shareable-data-pkg-" + flavor  
                

                shareablePkgDirString = os.path.join(shareableDirString,shareablePkgDirStemString)
                
                # get resource tracker entries - latest entry per resource id; no entry for removed resource ids
                resourceTrackerEntries = dsc_pkg_utils.get_tracker_entries(workingDataPkgDir=workingDataPkgDir,trackerType="resource-tracker",latestEntryOnly=True,includeRemovedEntry=False)
                
                # get version of resource tracker where all absolute paths (to resource and to resource dependencies) are 
                # converted to relative paths (relative to working data pkg dir)
                resourceTrackerEntriesTransformed = resourceTrackerEntries.copy()
                
                resourceTrackerEntriesTransformed["path"] = [os.path.relpath(p,workingDataPkgDir) for p in resourceTrackerEntriesTransformed["path"]]
                
                colWithPathList = list(resourceTrackerEntriesTransformed)
                colWithPathList = [c for c in colWithPathList if c.startswith("associatedFile")]
                colWithPathList = [c for c in colWithPathList if c not in ["associatedFileResultsDependOn","associatedFileMultiLikeFilesIds"]]
                print("colWithPathList: ",colWithPathList)
                for c in colWithPathList:
                    resourceTrackerEntriesTransformed[c] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(l) for l in resourceTrackerEntriesTransformed[c]]
                    resourceTrackerEntriesTransformed[c] = [[os.path.relpath(p,workingDataPkgDir) for p in l] if l else [] for l in resourceTrackerEntriesTransformed[c]]

                #trackerEntriesTransformed["associatedFileResultsDependOn"] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(l) for l in trackerEntriesTransformed[associatedFileResultsDependOn]]
                resourceTrackerEntriesTransformed["associatedFileResultsDependOn"] = [ast.literal_eval(l) for l in resourceTrackerEntriesTransformed["associatedFileResultsDependOn"]] # convert stringified list of dicts to actual list of dicts
                resourceTrackerEntriesTransformed["associatedFileResultsDependOn"] = [dsc_pkg_utils.relPathResultsDependOn(l, relToPath=workingDataPkgDir, pathKey="resultIdDependsOn") if l else [] for l in resourceTrackerEntriesTransformed["associatedFileResultsDependOn"]]  


                # get private date (access date) as a timestamp in order to be able to compare to today timestamp
                resourceTrackerEntries["accessDateTimeStamp"] = pd.to_datetime(resourceTrackerEntries["accessDate"])
                
                #-------------Open access calcs-----------------------------------------------------
                resourceTrackerEntriesContainOpenAccess = resourceTrackerEntries[resourceTrackerEntries["access"].str.contains("open-access")]
                print("resourceTrackerEntriesContainOpenAccess: ",resourceTrackerEntriesContainOpenAccess)
                
                # get df with open-access resources that never had temporary-private access also set (should be open access now) 
                resourceTrackerEntriesContainOpenAccessAndNOTTempPrivate = resourceTrackerEntriesContainOpenAccess[-resourceTrackerEntriesContainOpenAccess["access"].str.contains("temporary-private")]
                # get df with open-access resources that ALSO had temporary-private access set (only open access if today is >= private date)
                resourceTrackerEntriesContainOpenAccessAndTempPrivate = resourceTrackerEntriesContainOpenAccess[resourceTrackerEntriesContainOpenAccess["access"].str.contains("temporary-private")]
                
                # get df with resources past private date (should be open access now)
                resourceTrackerEntriesContainOpenAccessAndTempPrivatePastPrivateDate = resourceTrackerEntriesContainOpenAccessAndTempPrivate[resourceTrackerEntriesContainOpenAccessAndTempPrivate["accessDateTimeStamp"] <= pd.Timestamp("now").normalize()]
                # get df with resources NOT past private date (still private now)
                resourceTrackerEntriesContainOpenAccessAndTempPrivateNOTPastPrivateDate = resourceTrackerEntriesContainOpenAccessAndTempPrivate[resourceTrackerEntriesContainOpenAccessAndTempPrivate["accessDateTimeStamp"] > pd.Timestamp("now").normalize()]
                
                # get df with resources NOT past private date (still private now), but have an access date less or equal to user-specified "by-date" for open-access-by-date flavor of shareable data pkg
                resourceTrackerEntriesContainOpenAccessAndTempPrivateAccessDateBeforeByDate = resourceTrackerEntriesContainOpenAccessAndTempPrivate[resourceTrackerEntriesContainOpenAccessAndTempPrivate["accessDateTimeStamp"] <= pd.Timestamp(byDate).normalize()]
                
                # resources that are open access now are those that either 1) never had temp private access assigned, or 
                # 2) had temp private access assigned but today is >= the private/access date set by the user
                resourceTrackerEntriesOpenAccessNow = pd.concat([resourceTrackerEntriesContainOpenAccessAndNOTTempPrivate,resourceTrackerEntriesContainOpenAccessAndTempPrivatePastPrivateDate], axis=0)
                resourceTrackerEntriesOpenAccessByDate = pd.concat([resourceTrackerEntriesContainOpenAccessAndNOTTempPrivate,resourceTrackerEntriesContainOpenAccessAndTempPrivateAccessDateBeforeByDate], axis=0)
                
                #-------------Managed access calcs-----------------------------------------------------
                resourceTrackerEntriesContainManagedAccess = resourceTrackerEntries[resourceTrackerEntries["access"].str.contains("managed-access")]
                print("resourceTrackerEntriesContainManagedAccess: ",resourceTrackerEntriesContainManagedAccess)
                
                # get df with managed-access resources that never had temporary-private access also set (should be managed access now) 
                resourceTrackerEntriesContainManagedAccessAndNOTTempPrivate = resourceTrackerEntriesContainManagedAccess[-resourceTrackerEntriesContainManagedAccess["access"].str.contains("temporary-private")]
                # get df with managed-access resources that ALSO had temporary-private access set (only managed access if today is >= private date)
                resourceTrackerEntriesContainManagedAccessAndTempPrivate = resourceTrackerEntriesContainManagedAccess[resourceTrackerEntriesContainManagedAccess["access"].str.contains("temporary-private")]
                
                # get df with resources past private date (should be managed access now)
                resourceTrackerEntriesContainManagedAccessAndTempPrivatePastPrivateDate = resourceTrackerEntriesContainManagedAccessAndTempPrivate[resourceTrackerEntriesContainManagedAccessAndTempPrivate["accessDateTimeStamp"] <= pd.Timestamp("now").normalize()]
                # get df with resources NOT past private date (still private now)
                resourceTrackerEntriesContainManagedAccessAndTempPrivateNOTPastPrivateDate = resourceTrackerEntriesContainManagedAccessAndTempPrivate[resourceTrackerEntriesContainManagedAccessAndTempPrivate["accessDateTimeStamp"] > pd.Timestamp("now").normalize()]
                
                # get df with resources NOT past private date (still private now), but have an access date less or equal to user-specified "by-date" for managed-access-by-date flavor of shareable data pkg
                resourceTrackerEntriesContainManagedAccessAndTempPrivateAccessDateBeforeByDate = resourceTrackerEntriesContainManagedAccessAndTempPrivate[resourceTrackerEntriesContainManagedAccessAndTempPrivate["accessDateTimeStamp"] <= pd.Timestamp(byDate).normalize()]
                
                # resources that are managed access now are those that either 1) never had temp private access assigned, or 
                # 2) had temp private access assigned but today is >= the private/access date set by the user
                resourceTrackerEntriesOpenAccessNow = pd.concat([resourceTrackerEntriesContainOpenAccessAndNOTTempPrivate,resourceTrackerEntriesContainOpenAccessAndTempPrivatePastPrivateDate], axis=0)
                resourceTrackerEntriesOpenAccessByDate = pd.concat([resourceTrackerEntriesContainOpenAccessAndNOTTempPrivate,resourceTrackerEntriesContainOpenAccessAndTempPrivateAccessDateBeforeByDate], axis=0)
                
                resourceTrackerEntriesManagedAccessNow = pd.concat([resourceTrackerEntriesContainManagedAccessAndNOTTempPrivate,resourceTrackerEntriesContainManagedAccessAndTempPrivatePastPrivateDate], axis=0)
                resourceTrackerEntriesManagedAccessByDate = pd.concat([resourceTrackerEntriesContainManagedAccessAndNOTTempPrivate,resourceTrackerEntriesContainManagedAccessAndTempPrivateAccessDateBeforeByDate], axis=0)
                

                #-------------Set resources to keep-----------------------------------------------------

                if flavor == "open-access-now":
                    resourceTrackerEntriesToShare = resourceTrackerEntriesOpenAccessNow
                elif flavor == "open-access-by-date":
                    resourceTrackerEntriesToShare = resourceTrackerEntriesOpenAccessByDate
                elif flavor == "managed-access-now":
                    resourceTrackerEntriesToShare = pd.concat([resourceTrackerEntriesOpenAccessNow,resourceTrackerEntriesManagedAccessNow], axis=0)
                elif flavor == "managed-access-by-date":
                    resourceTrackerEntriesToShare = pd.concat([resourceTrackerEntriesOpenAccessByDate,resourceTrackerEntriesManagedAccessByDate], axis=0)
                else: 
                    print("a \"" + flavor + "\" flavor of shareable data pkg is not currently supported - please use one of the currently supported flavors: open-access-now, open-access-by-date, managed-access-now, managed-access-by-date")
                

                # get any results trackers that will be shared and convert full paths to relative paths
                if "heal-formatted-results-tracker" in resourceTrackerEntriesToShare["categorySubMetadata"].values:
                    resultsTrackerDf = resourceTrackerEntriesToShare[resourceTrackerEntriesToShare["categorySubMetadata"] == "heal-formatted-results-tracker"]
                    resultsTrackerList = resultsTrackerDf["path"].tolist()

                    resultsTrackerEntriesTransformedDfList = []
                    resultsTrackerStemList = []
                    for resultsTracker in resultsTrackerList: 
                        resultsTrackerStem = Path(resultsTracker).stem
                        resultsTrackerString = resultsTrackerStem.split("heal-csv-")[1]
                        resultsTrackerEntries = dsc_pkg_utils.get_tracker_entries(workingDataPkgDir=workingDataPkgDir,trackerType=resultsTrackerString,latestEntryOnly=True,includeRemovedEntry=False)

                        colWithPathList = list(resultsTrackerEntries)
                        colWithPathList = [c for c in colWithPathList if c.startswith("associatedFile")]
                        print("colWithPathList: ",colWithPathList)
                        for c in colWithPathList:
                            resultsTrackerEntries[c] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(l) for l in resultsTrackerEntries[c]]
                            resultsTrackerEntries[c] = [[os.path.relpath(p,workingDataPkgDir) for p in l] if l else [] for l in resultsTrackerEntries[c]]

                        resultsTrackerEntriesTransformedDfList.append(resultsTrackerEntries)
                        resultsTrackerStemList.append(resultsTrackerStem)


                filesToKeep = resourceTrackerEntriesToShare["path"].tolist()
                filesToKeep.extend([os.path.join(workingDataPkgDir,"heal-csv-experiment-tracker.csv")])
                filesToKeep = [Path(f) for f in filesToKeep]
                print("filesToKeep: ",filesToKeep)
                
                # create the shareable data pkg - filtering to keep only the files with the appropriate access level/data
                # as specified by the shareable data pkg "flavor"
                shutil.copytree(str(studyFolderDirPath),
                                shareablePkgDirString,
                                ignore=ignore_files_2(filesToKeep=filesToKeep))
                
                # resource tracker (transformed with full paths >> rel paths) is shared by default
                # results trackers (transformed with full paths >> rel paths) are shared only if access level is compatible with user specified shareable data pkg flavor
                resourceTrackerEntriesTransformed.to_csv(os.path.join(shareablePkgDirString,workingDataPkgDirStem,"heal-csv-resource-tracker.csv"),index=False)
                if resultsTrackerStemList:
                    for stem,df in zip(resultsTrackerStemList,resultsTrackerEntriesTransformedDfList):
                        fname = stem + ".csv"
                        df.to_csv(os.path.join(shareablePkgDirString,workingDataPkgDirStem,fname),index=False)
                
                creationMetadata = {
                    "createdTimestamp":[pd.Timestamp("now").normalize()],
                    "createdFlavor":[flavor]
                    }
                
                creationMetadataDf = pd.DataFrame(creationMetadata)
                if "by-date" in flavor:
                    creationMetadataDf["byDate"] = byDate

                creationMetadataDf.to_csv(os.path.join(shareablePkgDirString,workingDataPkgDirStem,"shareable-pkg-creation-metadata.csv"),index=False)
                return 


                # shutil.copytree(str(studyFolderDirPath),
                #                 shareableShellDirString,
                #                 ignore=ignore_files_2(workingDataPkgDir=workingDataPkgDir))

    
#createShareableDataPkgShell(workingDataPkgDir="C:/Users/tentner-andrea/Documents/vivli-test-study/dsc-pkg/")

#createShareableDataPkg(workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",flavor="shell")
#createShareableDataPkg(workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",flavor="open-access-now")

# filesToKeep = [
#     r"C:\Users\tentner-andrea\Documents\vivli-test-study\data\anonymized-analysis-dataset.dta",
#     r"C:\Users\tentner-andrea\Documents\vivli-test-study\code\anonymize.do.txt",
# ]

# createShareableDataPkg(
#     workingDataPkgDir="C:\\Users\\tentner-andrea\\Documents\\vivli-test-study\\dsc-pkg\\",
#     flavor="shell")

# createShareableDataPkg(
#     workingDataPkgDir="C:\\Users\\tentner-andrea\\Documents\\vivli-test-study\\dsc-pkg\\",
#     flavor="open-access-now")

# createShareableDataPkg(
#     workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",
#     flavor="shell")

createShareableDataPkg(
    workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",
    flavor="open-access-now")

createShareableDataPkg(
    workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",
    flavor="open-access-by-date",
    byDate="6/1/2024")

createShareableDataPkg(
    workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",
    flavor="managed-access-now")

createShareableDataPkg(
    workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",
    flavor="managed-access-by-date",
    byDate="6/1/2024")

createShareableDataPkg(
    workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/",
    flavor="managed-access-by-date",
    byDate="1/1/2025")

# print(hi["path"])
# print(hi["associatedFileDataDict"])







