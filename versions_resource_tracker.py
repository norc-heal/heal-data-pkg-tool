# step 1: add new fields, delete deprecated fields, rename fields 

# for each schema property:

# if deprecated is true
#   delete any field with current or former field name(s)
# if deprecated is false
#   if field with current field name exists
#       leave field with current field name alone
#       delete any field with a former field name
#   if field with current field name does not exist
#       if former field name(s)
#           if field with former field name exists
#               copy field with former field name and rename to current field name
#           if field with former field name does not exist
#               create new field with current field name
#       if no former field name(s)
#           create new field with current field name
#
# after looping through all schema properties with above,
# for all schema properties where deprecated is False, collect all former field names,
# and delete any fields with a former field name

# step 2: update enums

# for each (non-deprecated) schema property:

# if mapEnums is not empty
#   if enum value is in keys of mapEnums
#       replace enum value with value specified by corresponding key of mapEnums
#   if enum value is not in keys of mapEnums
#       replace enum value with empty/null
# if mapEnums is empty
#   do nothing

# step 3: update subfield names

# for each (non-deprecated) schema property:

# if formerSubNames is not empty
#   if value is a list of dictionaries
#       replace keys in list of dictionaries according to the mapping in formerSubNames
#       (https://stackoverflow.com/questions/54637847/how-to-change-dictionary-keys-in-a-list-of-dictionaries)




fieldNameMap = {
    "latestVersion":"0.3.0",
    "properties":{
        "schemaVersion":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "resourceId":{
            "formerNames": ["resource.id"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "path":{
            "formerNames":[],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "description":{
            "formerNames":[],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "category":{
            "formerNames":[],
            "deprecated": False,
            "mapEnum": {
                "publication":["multi-result"],
                "result":["single-result"]
            },
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "expBelongsTo":{
            "formerNames": ["exp.belongs.to"],
            "deprecated": True,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "experimentNameBelongsTo":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "name":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "title":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "descriptionFileNameConvention":{
            "formerNames": ["description.file.name.convention"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "descriptionFile":{
            "formerNames": ["description.file"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },    
        "descriptionRow":{
            "formerNames": ["description.row"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "categorySubMetadata":{
            "formerNames": ["category.sub.metadata"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum": ["heal-formatted-experiment-tracker"],
            "formerSubNames": {}
        },
        "categorySubMetadataOther":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "categorySubData":{
            "formerNames": ["category.sub.data"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        # "categorySubResults":{
        #     "formerNames": ["category.sub.results"],
        #     "deprecated": True,
        #     "mapEnum": {},
        #     "deleteEnum":[]
        # },
        "categorySubResult":{
            "formerNames": ["categorySubSingleResult","categorySubResults","category.sub.results"],
            "deprecated": False,
            "mapEnum": {
                "single-panel-figure":["figure"]
            },
            "deleteEnum":["draft-publication","publication","report","white-paper","presentation","poster"],
            "formerSubNames": {}
        },
        "categorySubPublication":{
            "formerNames": ["categorySubMultiResult","categorySubResults","category.sub.results"],
            "deprecated": False,
            "mapEnum": {
                "peer-review-manuscript":["publication","draft-publication"]
            },
            "deleteEnum":["figure","table","text"],
            "formerSubNames": {}
        },
        "associatedFileDataDict":{
            "formerNames": ["assoc.file.dd"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "associatedFileProtocol":{
            "formerNames": ["assoc.file.protocol"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "associatedFileResultsTracker":{
            "formerNames": ["assoc.file.result.tracker"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "associatedFileDependsOn":{
            "formerNames": ["assoc.file.depends.on"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "associatedFileResultsDependOn":{
            "formerNames": ["assoc.file.result.depends.on"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {
                "resultId":["result.id"],
                "resultIdDependsOn":["result.id.depends.on"]
            }
        },
        "associatedFileMultiLikeFiles":{
            "formerNames": ["assoc.file.multi.like.file"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "access":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {
                "open-access":["public"],
                "managed-access":["restricted-access"]
            },
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "accessDate":{
            "formerNames": ["access.date"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "format":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "softwareUsed":{
            "formerNames": ["format.software"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "profile":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "mediatype":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "encoding":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "schema":{
            "formerNames": [],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "resourceCreateDateTime":{
            "formerNames": ["resource.create.date.time"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "resourceModDateTime":{
            "formerNames": ["resource.mod.date.time"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "annotationCreateDateTime":{
            "formerNames": ["restrk.create.date.time"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "annotationModDateTime":{
            "formerNames": ["restrk.mod.date.time"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "resourceIdNumber":{
            "formerNames": ["resource.id.num"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "resourceModTimeStamp":{
            "formerNames": ["resource.mod.time.stamp"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        },
        "annotationModTimeStamp":{
            "formerNames": ["restrk.mod.time.stamp"],
            "deprecated": False,
            "mapEnum": {},
            "deleteEnum":[],
            "formerSubNames": {}
        }
    }
}