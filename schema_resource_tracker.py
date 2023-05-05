# used the regex from here to validate date: https://stackoverflow.com/questions/51224/regular-expression-to-match-valid-dates/8768241#8768241:~:text=To%20control%20a%20date%20validity%20under%20the%20following%20format%20%3A

# issue: use pydantic to require path to be a valid file path - maybe use https://stackoverflow.com/questions/60173776/check-with-jsonschema-if-path-is-valid
# issue: allow mutiple file refs in assoc.dd, assoc.protocol, assoc.id.map, and assoc.depends.on AND provide browse to file option implemented (currently can only implement browse to file for single value field)
# issue: make some fields depend on others - maybe use https://stackoverflow.com/questions/62690633/in-jsonschema-specific-field-is-required-based-on-value-of-another-field#:~:text=1-,Answer,-Sorted%20by%3A

schema_resource_tracker = {
    "type": "object",
    "description": "HEAL DSC Core Metadata piece to track and provide basic information about resource(s)/file(s) that support/are produced by/result from experiments you perform/will perform as part of your HEAL study.Objective is to list at least all files that will be submitted to a data repository in order to describe what each file is, how they relate to each other/how to use them, and how they relate to results/publications shared by the study group. Files may include results files (e.g. publications or draft publications/pieces of publications), processed and raw data files, protocol and analytic plan files, data dictionaries for tabular data files, other metadata as appropriate to data/field type, etc.",
    "title": "HEAL Resource Tracker",
    "properties": {
        "exp.belongs.to": {
            "title": "Experiment Belong To",
            "description": "if the file pertains specifically to one of the study experiments, list here; if the file pertains to more than one experiment, or to all experiments/the study as a whole, leave this blank; use experiment ID as assigned/formatted in your Experiment Tracker file here; prefix is 'exp-' followed by a number starting with 1 for the first experiment, and iterating by 1 for each successive experiment (i.e. exp-1, exp-2, etc.)",
            "type": "string",
            "pattern": "^exp-+-*[0-9]*[1-9][0-9]*$"
        },
        #"name": {
        #    "title" : "Resource Name",
        #    "description": "this will be auto-inferred as the file name part of the file path",
        #    "type": "string"
        #},
        "path": {
            "title": "Resource File Path",
            "description": "this will be auto-inferred as the full file path to resource",
            "type": "string"
        },
        "title": {
            "title": "Resource Title",
            "description": "human-readable title/name of resource",
            "type": "string"
        },
        "description": {
            "title": "Resource Description",
            "description": "description of resource",
            "type": "string"
        },
        "description.row": {
            "title": "Resource Row Description",
            "description": "for tabular data resource, row description; e.g. one row represents one subject at one timepoint",
            "type": "string"
        },
        "description.file": {
            "title": "Resource File Description",
            "description": "for multi-file resource containing multiple files of the same type, component file description",
            "type": "string"
        },
        "description.file.name.convention": {
            "title": "Resource File Name Convention Description",
            "description": "for multi-file resource containing multiple files of the same type, provide the naming convention of files (e.g. subject-xx-protocol-xxx-day-xxxxxxxx)",
            "type": "string"
        },
        "category": {
            "title" : "Resource Category",
            "description": "options are multi-result (a file that includes more than one result in the form of a figure, text, etc.), single result, data, metadata, code",
            "type": "string",
            "enum": ["","multi-result","single result","data","metadata","code"]
        },
        "category.sub.metadata": {
            "title" : "Metadata Resource - Sub-Category",
            "description": "",
            "type": "string",
            "enum": ["","data-dictionary","protocol","id-map","analysis plan","results-tracker","experiment-tracker"]
        },
        "category.sub.data": {
            "title" : "Data Resource - Sub-Category",
            "description": "",
            "type": "string",
            "enum": ["","raw","processed-intermediate","processed-final"]
        },
        "category.sub.results": {
            "title" : "Results Resource - Sub-Category",
            "description": "",
            "type": "string",
            "enum": ["","figure","text","draft publication","publication"]
        },
        "assoc.file.dd": {
            "title": "Data Resource - Associated Data Dictionary",
            "description": "generally relevant only for tabular data file resources; reference/file path to associated data dictionary file(s) - preferably in heal csv data dictionary format",
            "type": "string"
            #"type": "array",
            #"items": {
            #    "type": "string"
            #}
        },
        "assoc.file.protocol": {
            "title": "Data Resource - Associated Protocol",
            "description": "generally relevant only for data file resources; reference/file path to associated protocol file(s)",
            "type": "string"
            #"type": "array",
            #"items": {
            #    "type": "string"
            #}
        },
        "assoc.file.id.map": {
            "title": "Data Resource - Associated ID Map",
            "description": "generally relevant only for tabular data file resources; reference/file path to associated ID map file(s); e.g. if each row in a tabular data file represents a unique study subject at a unique study timepoint and the study subject is denoted by an ID in the data file, there may be an associated ID map that maps the subject ID to demographic variables relevant to each subject.",
            "type": "string"
            #"type": "array",
            #"items": {
            #    "type": "string"
            #}
        },
        "assoc.file.depends.on": {
            "title": "Source Files/Dependencies",
            "description": "if the current resource file has dependencies/if other files are necessary to make this file (e.g. raw data file necessary to  make processed data file) list them here; only one layer deep; can be data, code, protocol (?); if already listed under assoc.file.dd, assoc.file.protocol, or assoc.file.id.map no need to repeat here. Alternatively, can use this field as a catch-all instead of using those other more specific assoc.file fields.",
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "access": {
            "title" : "Access",
            "description": "What is the current/final access level anticipated for this resource? Options are permanent-private (current and final access level is private), temporary-private (current access level is private but final access level will be either restricted-access or public), restricted-access (either current or final access level will allow request of data with barriers/restrictions to access), public (either current or final access level will allow largely unrestricted request of/access to data); Many investigators will designate data as currently temporary-private, with a final access level of either restricted-access or public, in this case choose both temporary-private and either restricted-access or public, then add the date at which you expect to transition from temporary-private to either restricted-access or public in the Access Date field below; private means members of the public cannot request access; restricted access means they can request access but there is gate-keeping",
            "type": "array",
            "items":{
                "type": "string",
                "enum": ["","permanent-private","temporary-private","restricted-access","public"]
            }
        },
        "access.date": {
            "title": "Access Date (YYYY/MM/DD or YYYY-MM-DD)",
            "description": "If the resource file is currently being held as temporary-private access level and will transition to either restricted-access or public access level at some point, please provide an anticipated date at which this transition will occur - Best guesses are appreciated, however you will NOT be held to this date and may update this date at any time.",
            "type": "string",
            "pattern": "(((19|20)([2468][048]|[13579][26]|0[48])|2000)[/-]02[/-]29|((19|20)[0-9]{2}[/-](0[4678]|1[02])[/-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[/-](0[1359]|11)[/-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[/-](0[1-9]|1[0-9]|2[0-8])))"
        },
        #"format": {
        #    "title": "Format",
        #    "description": "auto inferred; e.g. csv",
        #    "type": "string"
        #},
        "format.software": {
            "title": "Software used to produce/read the resource file",
            "description": "if the format is proprietary and requires specific software to open/interpret, provide the software name and version; e.g. Origin 11.0, CorelDraw 5.6",
            "type": "string"
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
        #}
    }
}