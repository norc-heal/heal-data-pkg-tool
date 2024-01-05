


schema_results_tracker = {
    "type": "object",
    "description": "HEAL DSC Core Metadata piece to track and provide basic information about results statements or figures in a publication (e.g. a peer review manuscript, report, presentation, poster, etc.) that presents results from your HEAL study. Objective is to list at least all results that have been/will be published in order to describe each result, the data/non-data files each result depends on, and how to use these data/non-data files to reproduce published results.",
    "title": "HEAL Results Tracker",
    "version": "0.3.0",
    "properties": {
        "schemaVersion": {
            "title": "Schema version",
            "description": "Version of the overall schema (for each entry/row in the tracker) used at time of annotation; auto-populated equal to the value of the version key for the overall schema; should be constant for all rows in tracker.",
            "type": "string",
            "priority": "schema, auto"
        },
        "resultId": {
            "title": "Result ID",
            "description": "Unique ID assigned to each result; If using the DSC Data Packaging Tool to annotate your result(s), these IDs will be auto-assigned when you use the Add Result Tracker function. Auto-assignment of IDs occurs by searching you working Data Package Directory for any result annotation files already saved, identifying the result ID with the highest result ID number, and adding 1 to that number to get the result ID number and unique result ID for the current result.", 
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
            "enum": ["","single-panel-figure","figure-panel","table","text"],
            "priority": "all, high"
        },
        "experimentNameBelongsTo": {
            "title": "Experiment Result \"Belongs\" To",
            "description": "If the result pertains specifically to one of the study experiments (i.e. all data/observations/activities that underly this result came from a single study experiment or activity), list the experiment name for that experiment here; If the result pertains to more than one experiment, or to all experiments/the study as a whole, leave this blank; Use the experiment name as assigned/formatted in your Experiment Tracker file.",
            "type": "string",
            #"pattern": "^(?=.{3,50}$)[a-z]+(-*)([a-z0-9]+)(-[a-z,0-9]+)*$",
            "enum": ["default-experiment-name"],
            "priority": "all, low"
        },
        "associatedFilePublication": {
            "title": "Associated Publication",
            "description": "The publication(s) in which this result has been shared.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "all, high"
        },
        "figureNumber": {
            "title" : "Figure Number",
            "description": "If the result is a figure result, provide the number of the figure as it appears in the corresponding publication; For example, enter '1' for Figure Number if the result is being shared in a single panel figure called 'Figure 1'; Enter '1A' if the result is being shared in panel 'A' of a multi-panel figure called 'Figure 1'. If the result is included in more than one publication (e.g. the same figure may be shared in both a presentation and a peer-review manuscript), use the Associated Publication(s) field above to specify all publication files in which the result appears, and add the figure number at which the result appears in each of those files in this field, using the same order (e.g. file-1, file-2; figure-number-in-file-1, figure-number-in-file-2).",
            "type": "array",
            "items": {
                "type": "string"
            },
            "priority": "figure, high"
        },
        "tableNumber": {
            "title" : "Table Number",
            "description": "If the result is a table result, provide the number of the table as it appears in the corresponding publication; For example, enter '1' for Table Number if the result is being shared in a table called 'Table 1'. If the result is included in more than one publication (e.g. the same table may be shared in both a presentation and a peer-review manuscript), use the Associated Publication(s) field above to specify all publication files in which the result appears, and add the table number at which the result appears in each of those files in this field, using the same order (e.g. file-1, file-2; table-number-in-file-1, table-number-in-file-2).",
            "type": "array",
            "items": {
                "type": "string"
            },
            "priority": "table, high"
        },
        "associatedFileDependsOn": {
            "title": "Associated Files/Dependencies",
            "description": "Data and/or non-data supporting files the result depends upon (e.g. data, analysis plan/code, etc.). If you are using the DSC Data Packaging Tool and have many result dependencies to add, you can use the Add Multiple Result Dependencies button above the form to reveal an interface where you can drag and drop many files at once. Only list dependencies one layer deep; dependencies can be data, code, figure creation software files, etc.",
            "type": "array",
            "items": {
                "type": "string",
                "format": "path"
            },
            "priority": "all, high"
        },
        "resultSupports": {
            "title": "Result Supports",
            "description": "Describe a larger claim(s) that is/will be made in a publication that this result is used to support; This may be more relevant to basic science studies - An example: A study uses both a chemical inhibition and a siRNA knockdown approach to test the hypothesis that inhibiting the activity of a protein leads to decreased chronic pain phenotype. They share the results of these two experiments in a multi-panel figure labeled 'Figure 1' in a peer-review manuscript. They add these two results to a Results Tracker for this publication. The first result is entered with Figure Number '1A' and with description 'chemical inhibition of protein X with inhibitor Y leads to decreased chronic pain phenotype Z'. The second result is entered as Figure Number '1B' and the description is 'knockdown of protein X with siRNA Y leads to decreased chronic pain phenotype Z'; However, both results can be entered with a Result Supports entry of 'Inhibition of protein X leads to decrease chronic pain phenotype'; Other results from this study that perhaps use similar chemical inhibition or siRNA knockdown of protein X but a different chronic pain phenotype readout could similarly be shared with a Result Support entry identical to the first two results, as all of these experiments are supporting this larger claim that inhibiting protein X reduces chronic pain phenotype.",
            "type": "array",
            "items": {
                "type": "string",
                #"format": "path"
            },
            "priority": "all, low"
        },
        "annotationCreateDateTime": {
            "title": "Results tracker entry creation datetime",
            "description": "Date time at which the result annotation was created; auto-inferred",
            "type": "string",
            "priority": "results tracker, auto"
        },
        "annotationModDateTime": {
            "title": "Results tracker entry modification datetime",
            "description": "Date time at which the result annotation was last modified; auto-inferred",
            "type": "string",
            "priority": "results tracker, auto"
        },
        "resultIdNumber": {
            "title": "Result ID Number",
            "description": "Numeric part of the ID; autogenerated from ID; used for easy sorting by ID file", 
            "type": "integer",
            #"pattern": "^resource-+-*[0-9]*[1-9][0-9]*$",
            "priority": "results tracker, auto"
        },
        "annotationModTimeStamp": {
            "title": "Results tracker entry modification datetime timestamp",
            "description": "Date time at which the result annotation was last modified, converted to timestamp for easy sorting by datetime; auto-inferred",
            "type": "number",
            "priority": "results tracker, auto"
        }
    }
}



