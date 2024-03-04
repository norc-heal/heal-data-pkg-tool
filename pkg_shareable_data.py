# importing the shutil module
import shutil
 
# importing the os module
import os

import pathlib
from pathlib import Path

import dsc_pkg_utils
import pandas as pd



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

def createShareableDataPkg(workingDataPkgDir,flavor="shell",shareableDataPkgShellDir="",StudyFolderCentralized=True,workingDataPkgDirInStudyFolder=True):
    # calling the shutil.copytree() method and
    # passing the src,dst,and ignore parameter
    workingDataPkgDirPath = Path(workingDataPkgDir)
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
                shareableDirStemString = studyFolderDirStemString + "-shareable-data-pkgs"
                shareableDirString = os.path.join(studyFolderDirParentString,shareableDirStemString)
                if not os.path.exists(shareableDirString):
                    os.mkdir(shareableDirString)

                shareablePkgDirStemString = studyFolderDirStemString + "-shareable-data-pkg-" + flavor
                shareablePkgDirString = os.path.join(shareableDirString,shareablePkgDirStemString)
                
                if flavor == "shell":
                    shutil.copytree(str(studyFolderDirPath),
                                    shareablePkgDirString,
                                    ignore=ignore_files_1)
                elif flavor == "open-access-now":
                    trackerEntries = dsc_pkg_utils.get_tracker_entries(workingDataPkgDir=workingDataPkgDir,trackerType="resource-tracker",latestEntryOnly=True,includeRemovedEntry=False)
                    
                    # get private date (access date) as a timestamp in order to be able to compare to today timestamp
                    trackerEntries["accessDateTimeStamp"] = pd.to_datetime(trackerEntries["accessDate"])
                    
                    trackerEntriesContainOpenAccess = trackerEntries[trackerEntries["access"].str.contains("open-access")]
                    print("trackerEntriesContainOpenAccess: ",trackerEntriesContainOpenAccess)
                    
                    # get df with open-access resources that never had temporary-private access also set (should be open access now) 
                    trackerEntriesContainOpenAccessAndNOTTempPrivate = trackerEntriesContainOpenAccess[-trackerEntriesContainOpenAccess["access"].str.contains("temporary-private")]
                    # get df with open-access resources that ALSO had temporary-private access set (only open access if today is >= private date)
                    trackerEntriesContainOpenAccessAndTempPrivate = trackerEntriesContainOpenAccess[trackerEntriesContainOpenAccess["access"].str.contains("temporary-private")]
                    
                    # move this to the top so that all dfs have the private/access date timestamp column
                    # # get private date (access date) as a timestamp in order to be able to compare to today timestamp
                    # trackerEntriesContainOpenAccessAndTempPrivate["accessDateTimeStamp"] = pd.to_datetime(trackerEntriesContainOpenAccessAndTempPrivate["accessDate"])
                    
                    # get df with resources past private date (should be open access now)
                    trackerEntriesContainOpenAccessAndTempPrivatePastPrivateDate = trackerEntriesContainOpenAccessAndTempPrivate[trackerEntriesContainOpenAccessAndTempPrivate["accessDateTimeStamp"] <= pd.Timestamp("now").normalize()]
                    # get df with resources NOT past private date (still private now)
                    trackerEntriesContainOpenAccessAndTempPrivateNOTPastPrivateDate = trackerEntriesContainOpenAccessAndTempPrivate[trackerEntriesContainOpenAccessAndTempPrivate["accessDateTimeStamp"] > pd.Timestamp("now").normalize()]
                    
                    # resources that are open access now are those that either 1) never had temp private access assigned, or 
                    # 2) had temp private access assigned but today is >= the private/access date set by the user
                    trackerEntriesOpenAccessNow = pd.concat([trackerEntriesContainOpenAccessAndNOTTempPrivate,trackerEntriesContainOpenAccessAndTempPrivatePastPrivateDate], axis=0)
                    filesToKeep = trackerEntriesOpenAccessNow["path"].tolist()
                    filesToKeep.extend([os.path.join(workingDataPkgDir,"heal-csv-experiment-tracker.csv"),os.path.join(workingDataPkgDir,"heal-csv-resource-tracker.csv")])
                    filesToKeep = [Path(f) for f in filesToKeep]
                    print("filesToKeep: ",filesToKeep)
                    
                    shutil.copytree(str(studyFolderDirPath),
                                    shareablePkgDirString,
                                    ignore=ignore_files_2(filesToKeep=filesToKeep))


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






