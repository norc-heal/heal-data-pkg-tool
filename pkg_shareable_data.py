# importing the shutil module
import shutil
 
# importing the os module
import os

import pathlib
from pathlib import Path

import dsc_pkg_utils



# defining the function to ignore the files 
# if present in any folder that does not start with "dsc-pkg"
# when folder starts with dsc-pkg do NOT ignore the files for copying
def ignore_files_1(dir, files):
    
    dirStem = Path(dir)
    dirStem = dirStem.stem
    dirStemString = str(dirStem)

    #if not dirStemString.startswith("dsc-pkg"): # in this case subfolders in dsc pkg will not have files copied over
    if not "dsc-pkg" in dir: # in this case subfolders in dsc pkg should have files copied over
        return [f for f in files if os.path.isfile(os.path.join(dir, f))]
    else:
        return []

# defining the function to ignore the files 
# if present in any folder that does not start with "dsc-pkg"
# when folder starts with dsc-pkg do NOT ignore the files for copying
def ignore_files_2(dir, files, filesToKeep):
    
    dirStem = Path(dir)
    dirStem = dirStem.stem
    dirStemString = str(dirStem)

    #if not dirStemString.startswith("dsc-pkg"): # in this case subfolders in dsc pkg will not have files copied over
    if not "dsc-pkg" in dir: # in this case subfolders in dsc pkg should have files copied over
        filesToIgnore = [f for f in files if os.path.isfile(os.path.join(dir, f))]
        filesToIgnore = [f for f in filesToIgnore if os.path.join(dir, f) not in filesToKeep]
        return filesToIgnore
    else:
        return []

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

                shareableShellDirStemString = studyFolderDirStemString + "-shareable-data-pkg-shell"
                shareableShellDirString = os.path.join(shareableDirString,shareableShellDirStemString)
                
                if flavor == "shell":
                    shutil.copytree(str(studyFolderDirPath),
                                    shareableShellDirString,
                                    ignore=ignore_files_1)
                elif flavor == "open-access-now":
                    trackerEntries = dsc_pkg_utils.get_tracker_entries(workingDataPkgDir=workingDataPkgDir,trackerType="resource-tracker",latestEntryOnly=True,includeRemovedEntry=False)
                    
                    trackerEntriesContainOpenAccess = trackerEntries[trackerEntries["access"].str.contains("open-access")]
                    
                    trackerEntriesContainOpenAccessAndTempPrivate = trackerEntries[trackerEntries["access"].str.contains("temporary-private")]
                    trackerEntriesContainOpenAccessAndTempPrivatePastPrivateDate = trackerEntries[trackerEntries["access"].str.contains("temporary-private")]
                    

                    trackerEntriesContainOpenAccessAndNOTTempPrivate = trackerEntries[~trackerEntries["access"].str.contains("temporary-private")]
                    
                    shutil.copytree(str(studyFolderDirPath),
                                    shareableShellDirString,
                                    ignore=ignore_files_2(filesToKeep=filesToKeep))


                # shutil.copytree(str(studyFolderDirPath),
                #                 shareableShellDirString,
                #                 ignore=ignore_files_2(workingDataPkgDir=workingDataPkgDir))


#createShareableDataPkgShell(workingDataPkgDir="C:/Users/tentner-andrea/Documents/vivli-test-study/dsc-pkg/")
createShareableDataPkgShell(workingDataPkgDir="P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg/")