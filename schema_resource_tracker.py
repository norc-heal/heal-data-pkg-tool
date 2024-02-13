# used the regex from here to validate date: https://stackoverflow.com/questions/51224/regular-expression-to-match-valid-dates/8768241#8768241:~:text=To%20control%20a%20date%20validity%20under%20the%20following%20format%20%3A

# issue: use pydantic to require path to be a valid file path - maybe use https://stackoverflow.com/questions/60173776/check-with-jsonschema-if-path-is-valid
# issue: allow mutiple file refs in assoc.dd, assoc.protocol, assoc.id.map, and assoc.depends.on AND provide browse to file option implemented (currently can only implement browse to file for single value field)
# issue: make some fields depend on others - maybe use https://stackoverflow.com/questions/62690633/in-jsonschema-specific-field-is-required-based-on-value-of-another-field#:~:text=1-,Answer,-Sorted%20by%3A
# issue: get tooltip to work in form so that field description from schema shows up on mouse over of field name - maybe use https://github.com/agoose77/qt-jsonschema-form/blob/fc0faab5b2635449eef6e6e3fbda1352a6f28203/qt_jsonschema_form/widgets.py#L11:~:text=self.setToolTip(%22%22%20if%20error%20is%20None%20else%20error.message)%20%20%23%20TODO

# upon adding resource check for:
# if tabular data resource - info to create a dd, and come back to add ref to dd in this resource file
# if multi-result resource - info to create a results tracker, and come back to add ref to result tracker in this resource file
# if expBelongsTo experiment id does not have an experiment file - info to create an experiment file for that experiment
# if expBelongsTo is left as default - info to confirm that the resource pertains to more than one experiment or to the study as a whole rather than to one specific experiment
# if temporary-private is selected in access field, check that either managed-access or open-access is also selected as the final access state
# if temporary-private is selected in access field, check that accessDate has been changed from the default date and is a 'reasonable' date (e.g. within 5 years of current date?)
# maybe create an accessory file for each resource file with data on all of these checks so that we can programmatically bring to attention all resources that need additional attention (e.g. all tabular data files still missing data dictionaries)

from copy import deepcopy
import json

# formSubProps = \
#     ["resourceId", 
#     "path", 
#     "description", 
#     "category", 
#     "experimentNameBelongsTo",
#     "expBelongsTo", 
#     "title", 
#     "descriptionFileNameConvention", 
#     "descriptionFile",
#     "descriptionRow",
#     "categorySubMetadata",
#     "categorySubData",
#     "categorySubResults",
#     "associatedFileDataDict",
#     "associatedFileProtocol",
#     "associatedFileResultsTracker",
#     "associatedFileDependsOn",
#     "associatedFileResultsDependOn",
#     "associatedFileMultiLikeFiles",
#     "access",
#     "accessDate",
#     "softwareUsed"]


schema_resource_tracker = {
    "type": "object",
    "description": "HEAL DSC Core Metadata piece to track and provide basic information about resource(s)/file(s) that support/are produced by/result from experiments you perform/will perform as part of your HEAL study. The objective is to list at least all files that will be submitted to a data repository in order to describe what each file is, how they relate to each other/how to use them, and how they relate to results/publications shared by the study group. Files may include results files (e.g. publications or draft publications/pieces of publications), processed and raw data files, protocol and analytic plan files, data dictionaries for tabular data files, other metadata as appropriate to data/field type, etc.",
    "title": "HEAL Resource Tracker",
    "version": "0.4.0",
    "properties": {
        "schemaVersion": {
            "title": "Schema version",
            "description": "Version of the overall schema (for each entry/row in the tracker) used at time of annotation; auto-populated equal to the value of the schemaVersion key for the overall schema.",
            "type": "string",
            #"const": "v0.3.0",
            "priority": "schema, auto"
        },
        "resourceId": {
            "title": "Resource ID",
            "description": "Unique ID assigned to each resource file; If using the DSC Data Packaging Tool to annotate your resource(s), these IDs will be auto-assigned based on resources already existing in your working Data Package Directory. Auto-assignment of IDs occurs by searching the directory for any resource annotation files already saved, identifying the resource ID with the highest resource ID number, and adding 1 to that number to get the resource ID number and unique resource ID for the current resource.", 
            "type": "string",
            "pattern": "^resource-+-*[0-9]*[1-9][0-9]*$",
            "priority": "all, high, auto"
        },
        "path": {
            "title": "Resource File Path",
            "description": "The full file path to your resource file. If you are using the DSC Data Packaging Tool and would like to use a single form to annotate multiple 'like' files, click the 'Add Multiple like Files' button above the form and drag and drop all of the like files you want to annotate together in that box. The file path for the first of the file paths you dropped in the box will be added to this field.",
            "type": "string",
            "format": "path",
            "priority": "all, high"
        },
        "description": {
            "title": "Resource Description",
            "description": "A description of your resource. For resources that are part of a set of multiple 'like' files, provide a description of the multi-file resource here and use the Resource File Description field to provide any description specific to each/any one specific file in the set.",
            "type": "string",
            "priority": "all, high"
        },
        "category": {
            "title" : "Resource Category",
            "description": "Broad category your resource falls into; Generally, these categories are: results, data, metadata, code. However, the actual category options parse the categories just a bit finer (e.g. options for result resources include either 'result' or 'publication'; options for data resources include either 'tabular-data' or 'non-tabular-data').",
            "type": "string",
            "enum": ["","publication","result","tabular-data","non-tabular-data","metadata","code"],
            "priority": "all, high"
        },
        # "expBelongsTo": {
        #     "title": "Experiment Belongs To",
        #     "description": "If the file pertains specifically to one of the study experiments, list the experiment ID for that experiment here; If the file pertains to more than one experiment, or to all experiments/the study as a whole, leave this blank; Use the experiment ID as assigned/formatted in your Experiment Tracker file (prefix is 'exp-' followed by a number starting with 1 for the first experiment, and iterating by 1 for each successive experiment - i.e. exp-1, exp-2, etc.)",
        #     "type": "string",
        #     "pattern": "^exp-+-*[0-9]*[1-9][0-9]*$",
        #     "priority": "all, low"
        # },
        "experimentNameBelongsTo": {
            "title": "Experiment Resource \"Belongs\" To",
            "description": "If the resource pertains specifically to one of the study experiments (e.g. this resource may be a protocol for, data collected from, code used to analyze data from, a single study experiment or activity), list the experiment name for that experiment here; If the resource pertains to more than one experiment, or to all experiments/the study as a whole, leave this blank; Use the experiment name as assigned/formatted in your Experiment Tracker file.",
            "type": "string",
            #"pattern": "^(?=.{3,50}$)[a-z]+(-*)([a-z0-9]+)(-[a-z,0-9]+)*$",
            "enum": ["default-experiment-name"],
            "priority": "all, low, hide-minimal"
        },
        "name": {
            "title" : "Resource Name",
            "description": "File path stem; Auto-inferred from file path",
            "type": "string",
            "priority": "frictionless, auto"
        },
        "title": {
            "title": "Resource Title",
            "description": "Human-readable title/name of resource",
            "type": "string",
            "priority": "all, low, hide-minimal"
        },
        "descriptionFileNameConvention": {
            "title": "Resource File Name Convention",
            "description": "For multi-file resource containing multiple files of the same type (multiple 'like' files), provide the naming convention of the files (e.g. for a file set: [subject-01-protocol-A-day-2020-06-05.csv, subject-02-protocol-A-day-2020-06-05.csv, subject-02-protocol-B-day-2020-12-05.csv], you would specify the naming convention as: subject-{subject ID}-protocol-{protocol ID}-day-{date of measurment in YYYY-MM-DD}). If you are using the DSC Data Packaging Tool, you can use the Apply Name Convention button above the form to validate your name convention format and use a valid file name convention to generate a minimal 'Resource File Description' that is a minimal description specific to each file in the multi-file resource set.",
            "type": "string",
            "priority": "multiple like resource, high, hide-minimal"
        },
        "descriptionFile": {
            "title": "Resource File Description",
            "description": "For a multi-file resource containing multiple files of the same type (multiple 'like' files), a description specific to the specific current file that is a component of that multi-file set.",
            "type": "string",
            "priority": "multiple like resource, high, auto, hide-minimal"
        },
        "descriptionRow": {
            "title": "Resource Row Description",
            "description": "For a tabular data resource, a description of what one row in the tabular data resource represents; e.g. one row per subject per timepoint",
            "type": "string",
            "priority": "tabular data, high, hide-minimal"
        },
        "categorySubMetadata": {
            "title" : "Metadata Resource - Sub-Category",
            "description": "Sub-category for a metadata resource",
            "type": "string",
            "enum": ["","heal-formatted-data-dictionary","other-formatted-data-dictionary","protocol","analysis-plan","heal-formatted-results-tracker","other"],
            "priority": "metadata, high"
        },
        "categorySubMetadataOther": {
            "title" : "Metadata Resource - Sub-Category - Other",
            "description": "If you selected \"other\" as your metadata type/sub-category, please tell us what kind of metadata this is",
            "type": "string",
            #"enum": ["","heal-formatted-data-dictionary","other-formatted-data-dictionary","protocol","analysis-plan","heal-formatted-results-tracker","heal-formatted-experiment-tracker","other"],
            "priority": "subMetadataOther, high"
        },
        "categorySubData": {
            "title" : "Data Resource - Sub-Category",
            "description": "Sub-category for a data resource",
            "type": "string",
            "enum": ["","raw","processed-intermediate","processed-final"],
            "priority": "data, high"
        },
        "categorySubResult": {
            "title" : "Result Resource - Sub-Category",
            "description": "Sub-category for a result resource",
            "type": "string",
            "enum": ["","single-panel-figure","multi-panel-figure","table","text"],
            "priority": "result, high"
        },
        "categorySubPublication": {
            "title" : "Publication Resource - Sub-Category",
            "description": "Sub-category for a publication resource",
            "type": "string",
            "enum": ["","peer-review-manuscript","report","white-paper","presentation","poster"],
            "priority": "publication, high"
        },
        "associatedFileDataDict": {
            "title": "Associated Data Dictionary",
            "description": "For a tabular data file resources, a reference/file path to associated data dictionary file(s) - preferably in heal csv data dictionary format",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "tabular data, high"
        },
        "associatedFileProtocol": {
            "title": "Associated Protocol",
            "description": "For a data file resource, a reference/file path to associated protocol file(s)",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "data, high"
        },
        "associatedFileResultsTracker": {
            "title": "Associated Results Tracker",
            "description": "For a publication resource, a reference/file path to the associated HEAL-formatted Results Tracker file - HEAL-formatted Results Tracker is a file that inventories each result in a publication (e.g. a peer-review-manuscript, report, presentation, poster, etc.), along with the data and other supporting files that underly/support each result. If you are using the DSC Data Packaging Desktop Tool, you can head to the Results Tracker tab of the tool to create a HEAL-formatted Results Tracker for your publication(s).",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "publication, high"
        },
        #"assoc.file.id.map": {
        #    "title": "Data Resource - Associated ID Map",
        #    "description": "generally relevant only for tabular data file resources; reference/file path to associated ID map file(s); e.g. if each row in a tabular data file represents a unique study subject at a unique study timepoint and the study subject is denoted by an ID in the data file, there may be an associated ID map that maps the subject ID to demographic variables relevant to each subject.",
        #    #"type": "string"
        #    "type": "array",
        #    "items": {
        #        "type": "string",
        #        "format": "path"
        #    }
        #},
        "associatedFileDependsOn": {
            "title": "Associated Files/Dependencies",
            "description": "For all resource files, if the current resource file has dependencies/if other files are necessary to make this file (e.g. raw data file necessary to make processed data file), or to interpret/understand this file (e.g. protocol, analysis plan, etc.), list them here; only list dependencies one layer deep; dependencies can be data, code, protocol, etc.; if already listed under a more specialized fields such as associatedFileDataDict, associatedFileProtocol, no need to repeat here.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "all, high, not results-tracker, not publication"
        },
        "associatedFileResultsDependOn": {
            "title": "Result-tracker - Associated Files/Dependencies",
            "description": "If the current resource file is a heal formatted result tracker (an file that inventories each of the results in a publication), use this field to list each result in the tracker along with its corresponding dependencies (i.e. files the result depends on, or are necessary to make/reach/interpret the result); for each result, only list dependencies one layer deep; dependencies can be data, code, protocol, etc.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "resultId": {
                        "type": "string"
                    },
                    "resultIdDependsOn": {
                        "type": "array",
                        #"format": "path"
                    }
                }
            },
            "priority": "only results-tracker, permanent hide "
        },
        "associatedFileMultiLikeFiles": {
            "title": "Multiple 'like' File Resource - File Paths",
            "description": "If the current resource file is annotating a resource that is one of multiple 'like' files, this field will list the file paths of all files that are part of the set of multiple 'like' file resources.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "multiple like resource, high, auto, permanent hide"
        },
        "associatedFileMultiLikeFilesIds": {
            "title": "Multiple 'like' File Resource - File Resource IDs",
            "description": "If the current resource file is annotating a resource that is one of multiple 'like' files, this field will list the resource IDs for all files that are part of the set of multiple 'like' file resources.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "multiple like resource, high, auto, permanent hide"
        },
        #"assoc.file.multi.depend": {
        #    "title": "Multiple Resource Dependencies",
        #    "description": "if the current resource file has many dependencies, it is not convenient to enter them by browsing for each dependency file one by one using the Associated Files/Dependencies form field; Instead, use the drag and drop file box at the top of the form that is revealed by clicking the Add Multiple Resource Dependencies button at the top of the form; adding dependency files in that box will populate this field with the list of all dependency files added in the box.",
        #    "type": "array",
        #    "items": {
        #        "type": "string",
        #        "format": "path"
        #    },
        #    "priority": "multiple dependencies, high, auto, permanent hide"
        #},
        "access": {
            "title" : "Access",
            "description": "What is the current/final access level anticipated for this resource? Options are permanent-private (current and final access level is private), temporary-private (current access level is private but final access level will be either managed-access or open-access), managed-access (current, final, or current AND final access level will allow request of data with barriers/restrictions to access), open-access (current, final, or current AND final access level will allow largely unrestricted request of/access to data); Many investigators will designate data as currently temporary-private, with a final access level of either managed-access or open-access: In this case choose both temporary-private AND either 1) managed-access or 2) open-access, then add the date at which you expect to transition from temporary-private to either managed-access or open-access in the Access Date field below; Private means members of the public cannot request access; Restricted access means they can request access but there is gate-keeping; Open access means they can often access the data without requesting access from a gate-keeper, and with minimal barriers to access.",
            "type": "array",
            "items":{
                "type": "string",
                "enum": ["","permanent-private","temporary-private","managed-access","open-access"]
            },
            "priority": "all, high, hide-minimal"
        },
        "accessDate": {
            "title": "Access Date (YYYY/MM/DD or YYYY-MM-DD)",
            "description": "If the resource file is currently being held as temporary-private access level and will transition to either managed-access or open-access access level at some point, please provide an anticipated date at which this transition will occur - Best guesses are appreciated, however you will NOT be held to this date and may update this date at any time.",
            "type": "string",
            "pattern": "(((19|20)([2468][048]|[13579][26]|0[48])|2000)[/-]02[/-]29|((19|20)[0-9]{2}[/-](0[4678]|1[02])[/-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[/-](0[1359]|11)[/-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[/-](0[1-9]|1[0-9]|2[0-8])))",
            "priority": "temporary private, high"
        },
        "format": {
            "title": "Format",
            "description": "auto inferred; e.g. csv",
            "type": "string",
            "priority": "frictionless, auto"
        },
        "softwareUsed": {
            "title": "Software used to produce/read the resource file",
            "description": "If the file format of the resource file is proprietary and requires specific software to open/interpret, provide the software name and version used by the study group to produce/work with the file; e.g. Origin 11.0, CorelDraw 5.6",
            "type": "string",
            "priority": "all, low, hide-minimal"
        },
        #"format.open.type": {
        #    "title": "Format Open Type",
        #    "description": "If the format is proprietary but can be opened/converted to open source format using open source tools, provide the open source format to which the file can be converted (e.g. csv)",
        #    "type": "string"
        #},
        #"format.open.protocol": {
        #    "title": "Format Open Protocol",
        #    "description": "If the format is proprietary but can be opened/converted to open source format using open source tools, provide the open source tools required and the protocol for converting the file to an open source format (open in excel, specify space delimited, 3 line header)",
        #    "type": "string"
        #},
        "profile": {
            "title": "Profile",
            "description": "auto inferred; e.g. tabular-data-resource",
            "type": "string",
            "priority": "frictionless, auto"
        },
        "mediatype": {
            "title": "Media Type",
            "description": "auto inferred; e.g. text/csv",
            "type": "string",
            "priority": "frictionless, auto"
        },
        "encoding": {
            "title": "Encoding",
            "description": "auto inferred; e.g. utf-8",
            "type": "string",
            "priority": "frictionless, auto"
        },
        "schema": {
            "title": "Schema",
            "description": "auto inferred; for tabular resource, schema of fields contained in tabular resource; might replace this with ref to either heal csv dd or heal json dd",
            "type": "string",
            "priority": "frictionless, auto"
        },
        "resourceCreateDateTime": {
            "title": "Resource creation datetime",
            "description": "Date time of resource creation; auto-inferred",
            "type": "string",
            "priority": "resource tracker, auto"
        },
        "resourceModDateTime": {
            "title": "Resource modification datetime",
            "description": "Date time at which the resource was last modified; auto-inferred",
            "type": "string",
            "priority": "resource tracker, auto"
        },
        "annotationCreateDateTime": {
            "title": "Resource tracker entry creation datetime",
            "description": "Date time at which the resource annotation was created; auto-inferred",
            "type": "string",
            "priority": "resource tracker, auto"
        },
        "annotationModDateTime": {
            "title": "Resource tracker entry modification datetime",
            "description": "Date time at which the resource annotation was last modified; auto-inferred",
            "type": "string",
            "priority": "resource tracker, auto"
        },
        "resourceIdNumber": {
            "title": "Resource ID Number",
            "description": "Numeric part of the ID; autogenerated from ID; used for easy sorting by ID file", 
            "type": "integer",
            #"pattern": "^resource-+-*[0-9]*[1-9][0-9]*$",
            "priority": "resource tracker, auto"
        },
        "resourceModTimeStamp": {
            "title": "Resource modification datetime timestamp",
            "description": "Date time at which the resource was last modified, converted to timestamp for easy sorting on datetime; auto-inferred",
            "type": "number",
            "priority": "resource tracker, auto"
        },
        "annotationModTimeStamp": {
            "title": "Resource tracker entry modification datetime timestamp",
            "description": "Date time at which the resource annotation was last modified, converted to timestamp for easy sorting by datetime; auto-inferred",
            "type": "number",
            "priority": "resource tracker, auto"
        },
        "removed": {
            "title": "Removed status",
            "description": "True if user has removed the resource from the scope of the data package",
            "type": "integer",
            "enum": [0,1],
            "priority": "resource tracker, auto"
        }
        
    }
}

# subProps = formSubProps

# allKeys = list(schema_resource_tracker["properties"].keys())
# #print(allKeys)

# keysToRemove = [x for x in allKeys if x not in subProps]
# #print(keysToRemove)

# form_schema_resource_tracker = deepcopy(schema_resource_tracker)

# for k in keysToRemove:
#     form_schema_resource_tracker["properties"].pop(k)

# #print(form_schema_resource_tracker)



