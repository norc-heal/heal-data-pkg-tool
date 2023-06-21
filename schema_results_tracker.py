


schema_results_tracker = {
    "type": "object",
    "description": "HEAL DSC Core Metadata piece to track and provide basic information about results statements or figures in a multi-result file (e.g. a publication) that presents results from your HEAL study. Objective is to list at least all results that have been/will be published in order to describe each result, the data/non-data files each result depends on, and how to use these data/non-data files to reproduce published results.",
    "title": "HEAL Results Tracker",
    "properties": {
        "result.id": {
            "title": "Result ID",
            "description": "Unique ID assigned to each result; If using the DSC Packaging application to annotate your resource(s), these IDs will be auto-assigned when you use the Add Result Tracker button above the form to add your Result Tracker Directory. Auto-assignment of IDs occurs by searching the directory for any result annotation files already saved, identifying the result ID with the highest result ID number, and adding 1 to that number to get the result ID number and unique result ID for the current result.", 
            "type": "string",
            "pattern": "^result-+-*[0-9]*[1-9][0-9]*$",
            "priority": "all, high, auto"
        },
        "description": {
            "title": "Result Description",
            "description": "A description of your result. For figure results this may be the figure caption. For text results, it is recommended that this text be identical or very similar to the text of result as shared in text of the multi-result file that is published or provided as part of the data package.",
            "type": "string",
            "priority": "all, high"
        },
        "category": {
            "title" : "Result Category",
            "description": "Broad category your result falls into; Generally, these categories are: figure, or text.",
            "type": "string",
            "enum": ["","figure","text"],
            "priority": "all, high"
        },
        "figure.number": {
            "title" : "Result - Figure Number",
            "description": "If the result is a figure result, provide the number of the figure as it appears in the corresponding multi-result file; Examples include '1' if the result is in figure 1, or '1a' if the result is in figure 1A.",
            "type": "string",
            "priority": "all, high"
        },
        "assoc.file.result.depends.on": {
            "title": "Associated Files/Dependencies",
            "description": "Data and/or non-data supporting files the result depends upon (e.g. data, analysis plan/code, etc.). If documenting resources wholistically (i.e. documenting all resources related to a study), only list dependencies one layer deep; if documenting resources minimally (i.e. only documenting resources that will be publicly shared), list dependencies liberally; dependencies can be data, code, protocol, etc.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "all, high"
        },
        "result.supports": {
            "title": "Result Supports",
            "description": "Describe a larger claim(s) that this result is used to support in text that is published or provided as part of the data package",
            "type": "array",
            "items": {
                "type": "string",
                #"format": "path"
            },
            "priority": "all, low"
        }
    }
}



