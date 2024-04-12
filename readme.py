import yaml

with open("./readme.yaml","r") as file:
    contents = yaml.safe_load(file)

print(contents)
contents["Get-started"]["Description"] = "hello"

pkgList = contents["Get-started"]["Contents"]["shareable-data-packages"]
addPkg = pkgList[0]
print(addPkg)
addPkg["shareable-data-package"]["package-name"] = "blahblah"
pkgList.append(addPkg)
contents["Get-started"]["Contents"]["shareable-data-packages"] = pkgList 

print(contents)












