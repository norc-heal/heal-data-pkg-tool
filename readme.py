import yaml

with open("./readme.yaml","r") as file:
    contents = yaml.safe_load(file)

pkgName = "example-shareable-data-package-name-2"

#print(contents)
contents["Get-started"]["Description"] = "hello"

pkgList = contents["Get-started"]["Contents"]["shareable-data-packages"]
print("pkgList: ",pkgList)
pkgListCopy = pkgList.copy()
print("pkgListCopy: ",pkgList)
addPkg = pkgListCopy[0].copy()
addPkg[pkgName] = addPkg.pop("example-shareable-data-package-name-1")
print("addPkg: ", addPkg)
# addPkg["shareable-data-package"]["package-name"] = "blahblah"
# print("addPkg: ", addPkg)
pkgList.append(addPkg)
print("pkgList: ",pkgList)
# contents["Get-started"]["Contents"]["shareable-data-packages"] = pkgList 
# print("pkgList: ",pkgList)
# print(contents)
# print("pkgList second element: ",pkgList[1])
# pkgList[1]["shareable-data-package"]["package-name"] = "blahblah"
# print("pkgList: ",pkgList)












