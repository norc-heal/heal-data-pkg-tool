import yaml
import copy
import pandas as pd
import os
from os import path

def createReadme(shareableDirString,shareablePkgDirStemString,flavor,byDate,sharedColString):

    readmePath = os.path.join(shareableDirString,"readme.yaml")
    
    bundleDir = path.abspath(path.dirname(__file__))
    readmeTemplatePath = path.join(bundleDir, "readme.yaml")

    # if there's already a readme, add to it
    # if not, start with the template readme
    if os.path.isfile(readmePath):
        startTemplateReadmePath = readmePath
    else:
        startTemplateReadmePath = readmeTemplatePath
    
    with open(startTemplateReadmePath,"r") as file:
        contents = yaml.safe_load(file)

    #pkgName = "example-shareable-data-package-name-2"
    pkgName = shareablePkgDirStemString



    #print(contents)
    #contents["Get-started"]["Description"] = "hello"

    pkgList = contents["Get-started"]["Contents"]["shareable-data-packages"]
    print("pkgList: ",pkgList)
    #pkgListCopy = pkgList.copy()
    pkgListCopy = copy.deepcopy(pkgList)
    print("pkgListCopy: ",pkgList)
    #addPkg = pkgListCopy[0].copy()
    addPkg = copy.deepcopy(pkgListCopy[0])

    if "example-shareable-data-package-name-1" in addPkg:
        print("example")
        example = True
    else:
        print("not example")
        example = False

        
    oldPkgName = list(addPkg.keys())
    oldPkgName = oldPkgName[0]
    addPkg[pkgName] = addPkg.pop(oldPkgName)
    addPkg[pkgName]["file-name"] = pkgName + ".zip"
    addPkg[pkgName]["access-regime"] = flavor
    if "by-date" in flavor:
        addPkg[pkgName]["by-date"] = byDate
    else: 
        addPkg[pkgName]["by-date"] = None
    addPkg[pkgName]["created"] = str(pd.Timestamp("now").normalize())
    addPkg[pkgName]["resource-tracker-flag-name"] = sharedColString

    print("addPkg: ", addPkg)
    print("pkgListCopy: ",pkgList)
    print("pkgList: ",pkgList)
    # addPkg["shareable-data-package"]["package-name"] = "blahblah"
    # print("addPkg: ", addPkg)

    if example:
        print("this is an example")
        pkgList[0] = addPkg
    else: 
        print("this is not an example")
        pkgList.append(addPkg)
    print("pkgList: ",pkgList)
    # contents["Get-started"]["Contents"]["shareable-data-packages"] = pkgList 
    # print("pkgList: ",pkgList)
    # print(contents)
    # print("pkgList second element: ",pkgList[1])
    # pkgList[1]["shareable-data-package"]["package-name"] = "blahblah"
    # print("pkgList: ",pkgList)

    #contents["Get-started"]["Contents"]["shareable-data-packages"][1]["example-shareable-data-package-name-2"]["access-regime"] = "hi"
    print("contents: ",contents)

    
    with open(readmePath,"w") as file:
        yaml.safe_dump(contents,file,sort_keys=False)
    print("finished writing readme")
    return












