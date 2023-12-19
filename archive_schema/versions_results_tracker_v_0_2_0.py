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
    "latestVersion":"0.2.0",
    "properties":{
        "resultId":{
            "formerNames": ["result.id"],
            "deprecated": False
        },
        "description":{
            "formerNames":[],
            "deprecated": False
        },
        "category":{
            "formerNames":[],
            "deprecated": False
        },
        "experimentNameBelongsTo":{
            "formerNames": [],
            "deprecated": False
        },
        "associatedFileMultiResultFile":{
            "formerNames": ["assoc.multi.result.file"],
            "deprecated": False
        },
        "figureNumber":{
            "formerNames": ["figure.number"],
            "deprecated": False
        },
        "tableNumber":{
            "formerNames": ["table.number"],
            "deprecated": False
        },
        "associatedFileDependsOn":{
            "formerNames": ["assoc.file.depends.on"],
            "deprecated": False
        },
        "resultSupports":{
            "formerNames": ["result.supports"],
            "deprecated": False
        },
        "annotationCreateDateTime":{
            "formerNames": ["restrk.create.date.time"],
            "deprecated": False
        },
        "annotationModDateTime":{
            "formerNames": ["restrk.mod.date.time"],
            "deprecated": False
        }
    }
}