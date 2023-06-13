# used the regex from here to validate date: https://stackoverflow.com/questions/51224/regular-expression-to-match-valid-dates/8768241#8768241:~:text=To%20control%20a%20date%20validity%20under%20the%20following%20format%20%3A

# issue: use pydantic to require path to be a valid file path - maybe use https://stackoverflow.com/questions/60173776/check-with-jsonschema-if-path-is-valid
# issue: allow mutiple file refs in assoc.dd, assoc.protocol, assoc.id.map, and assoc.depends.on AND provide browse to file option implemented (currently can only implement browse to file for single value field)
# issue: make some fields depend on others - maybe use https://stackoverflow.com/questions/62690633/in-jsonschema-specific-field-is-required-based-on-value-of-another-field#:~:text=1-,Answer,-Sorted%20by%3A
# issue: get tooltip to work in form so that field description from schema shows up on mouse over of field name - maybe use https://github.com/agoose77/qt-jsonschema-form/blob/fc0faab5b2635449eef6e6e3fbda1352a6f28203/qt_jsonschema_form/widgets.py#L11:~:text=self.setToolTip(%22%22%20if%20error%20is%20None%20else%20error.message)%20%20%23%20TODO

# upon adding resource check for:
# if tabular data resource - info to create a dd, and come back to add ref to dd in this resource file
# if multi-result resource - info to create a result tracker, and come back to add ref to result tracker in this resource file
# if exp.belongs.to experiment id does not have an experiment file - info to create an experiment file for that experiment
# if exp.belongs.to is left as default - info to confirm that the resource pertains to more than one experiment or to the study as a whole rather than to one specific experiment
# if temporary-private is selected in access field, check that either restricted-access or public is also selected as the final access state
# if temporary-private is selected in access field, check that access.date has been changed from the default date and is a 'reasonable' date (e.g. within 5 years of current date?)
# maybe create an accessory file for each resource file with data on all of these checks so that we can programmatically bring to attention all resources that need additional attention (e.g. all tabular data files still missing data dictionaries)

form_schema_resource_tracker = {
    "type": "object",
    "description": "HEAL DSC Core Metadata piece to track and provide basic information about resource(s)/file(s) that support/are produced by/result from experiments you perform/will perform as part of your HEAL study.Objective is to list at least all files that will be submitted to a data repository in order to describe what each file is, how they relate to each other/how to use them, and how they relate to results/publications shared by the study group. Files may include results files (e.g. publications or draft publications/pieces of publications), processed and raw data files, protocol and analytic plan files, data dictionaries for tabular data files, other metadata as appropriate to data/field type, etc.",
    "title": "HEAL Resource Tracker",
    "properties": {
        "resource.id": {
            "title": "Resource ID",
            "description": "resource id; auto-assigned", 
            "type": "string",
            "pattern": "^resource-+-*[0-9]*[1-9][0-9]*$",
            "priority": "all, high"
        },
        "path": {
            "title": "Resource File Path",
            "description": "this will be auto-inferred as the full file path to resource",
            "type": "string",
            "format": "path",
            "priority": "all, high"
        },
        "description": {
            "title": "Resource Description",
            "description": "description of resource",
            "type": "string",
            "priority": "all, high"
        },
        "category": {
            "title" : "Resource Category",
            "description": "options are multi-result (a file that includes more than one result in the form of a figure, text, etc.), single result, data, metadata, code",
            "type": "string",
            "enum": ["","multi-result","single result","tabular data","non-tabular data","metadata","code"],
            "priority": "all, high"
        },
        "exp.belongs.to": {
            "title": "Experiment Belongs To",
            "description": "if the file pertains specifically to one of the study experiments, list here; if the file pertains to more than one experiment, or to all experiments/the study as a whole, leave this blank; use experiment ID as assigned/formatted in your Experiment Tracker file here; prefix is 'exp-' followed by a number starting with 1 for the first experiment, and iterating by 1 for each successive experiment (i.e. exp-1, exp-2, etc.)",
            "type": "string",
            "pattern": "^exp-+-*[0-9]*[1-9][0-9]*$",
            "priority": "all, low"
        },
        #"name": {
        #    "title" : "Resource Name",
        #    "description": "this will be auto-inferred as the file name part of the file path",
        #    "type": "string"
        #},
        "title": {
            "title": "Resource Title",
            "description": "human-readable title/name of resource",
            "type": "string",
            "priority": "all, low"
        },
        "description.row": {
            "title": "Resource Row Description",
            "description": "for tabular data resource, row description; e.g. one row represents one subject at one timepoint",
            "type": "string",
            "priority": "tabular data"
        },
        "description.file.name.convention": {
            "title": "Resource File Name Convention",
            "description": "for multi-file resource containing multiple files of the same type, provide the naming convention of files (e.g. subject-xx-protocol-xxx-day-xxxxxxxx)",
            "type": "string",
            "priority": "multiple like resource"
        },
        "description.file": {
            "title": "Resource File Description",
            "description": "for multi-file resource containing multiple files of the same type, component file description",
            "type": "string",
            "priority": "multiple like resource"
        },
        "category.sub.metadata": {
            "title" : "Metadata Resource - Sub-Category",
            "description": "",
            "type": "string",
            "enum": ["","data-dictionary","protocol","id-map","analysis plan","results-tracker","experiment-tracker"],
            "priority": "metadata"
        },
        "category.sub.data": {
            "title" : "Data Resource - Sub-Category",
            "description": "",
            "type": "string",
            "enum": ["","raw","processed-intermediate","processed-final"],
            "priority": "data"
        },
        "category.sub.results": {
            "title" : "Results Resource - Sub-Category",
            "description": "",
            "type": "string",
            "enum": ["","figure","text","draft publication","publication"],
            "priority": "results"
        },
        "assoc.file.dd": {
            "title": "Associated Data Dictionary",
            "description": "generally relevant only for tabular data file resources; reference/file path to associated data dictionary file(s) - preferably in heal csv data dictionary format",
            #"type": "string"
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "tabular data"
        },
        "assoc.file.protocol": {
            "title": "Associated Protocol",
            "description": "generally relevant only for data file resources; reference/file path to associated protocol file(s)",
            #"type": "string"
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "data"
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
        "assoc.file.depends.on": {
            "title": "Other Associated Files/Dependencies",
            "description": "if the current resource file has dependencies/if other files are necessary to make this file (e.g. raw data file necessary to  make processed data file) list them here; only one layer deep; can be data, code, protocol (?); if already listed under assoc.file.dd, assoc.file.protocol, or assoc.file.id.map no need to repeat here. Alternatively, can use this field as a catch-all instead of using those other more specific assoc.file fields.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "all, high"
        },
        "access": {
            "title" : "Access",
            "description": "What is the current/final access level anticipated for this resource? Options are permanent-private (current and final access level is private), temporary-private (current access level is private but final access level will be either restricted-access or public), restricted-access (either current or final access level will allow request of data with barriers/restrictions to access), public (either current or final access level will allow largely unrestricted request of/access to data); Many investigators will designate data as currently temporary-private, with a final access level of either restricted-access or public, in this case choose both temporary-private and either restricted-access or public, then add the date at which you expect to transition from temporary-private to either restricted-access or public in the Access Date field below; private means members of the public cannot request access; restricted access means they can request access but there is gate-keeping",
            "type": "array",
            "items":{
                "type": "string",
                "enum": ["","permanent-private","temporary-private","restricted-access","public"]
            },
            "priority": "all, high"
        },
        "access.date": {
            "title": "Access Date (YYYY/MM/DD or YYYY-MM-DD)",
            "description": "If the resource file is currently being held as temporary-private access level and will transition to either restricted-access or public access level at some point, please provide an anticipated date at which this transition will occur - Best guesses are appreciated, however you will NOT be held to this date and may update this date at any time.",
            "type": "string",
            "pattern": "(((19|20)([2468][048]|[13579][26]|0[48])|2000)[/-]02[/-]29|((19|20)[0-9]{2}[/-](0[4678]|1[02])[/-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[/-](0[1359]|11)[/-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[/-](0[1-9]|1[0-9]|2[0-8])))",
            "priority": "temporary private"
        },
        #"format": {
        #    "title": "Format",
        #    "description": "auto inferred; e.g. csv",
        #    "type": "string"
        #},
        "format.software": {
            "title": "Software used to produce/read the resource file",
            "description": "if the format is proprietary and requires specific software to open/interpret, provide the software name and version; e.g. Origin 11.0, CorelDraw 5.6",
            "type": "string",
            "priority": "all, low"
        }
        #,
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
        #"profile": {
        #    "title": "Profile",
        #    "description": "auto inferred; e.g. tabular-data-resource",
        #    "type": "string"
        #},
        #"mediatype": {
        #    "title": "Media Type",
        #    "description": "auto inferred; e.g. text/csv",
        #    "type": "string"
        #},
        #"encoding": {
        #    "title": "Encoding",
        #    "description": "auto inferred; e.g. utf-8",
        #    "type": "string"
        #},
        #"schema": {
        #    "title": "Schema",
        #    "description": "auto inferred; for tabular resource, schema of fields contained in tabular resource; might replace this with ref to either heal csv dd or heal json dd",
        #    "type": "string"
        #},
        #"resource.create.date.time": {
        #    "title": "Resource creation datetime",
        #    "description": "Date time of resource creation; auto-inferred",
        #    "type": "string"
        #},
        #"resource.mod.date.time": {
        #    "title": "Resource modification datetime",
        #    "description": "Date time at which the resource was last modified; auto-inferred",
        #    "type": "string"
        #},
        #"restrk.create.date.time": {
        #    "title": "Resource tracker entry creation datetime",
        #    "description": "Date time at which the resource tracker file for the resource was created; auto-inferred",
        #    "type": "string"
        #},
        #"restrk.mod.date.time": {
        #    "title": "Resource tracker entry modification datetime",
        #    "description": "Date time at which the resource tracker file for the resource was last modified; auto-inferred",
        #    "type": "string"
        #}
    }
}