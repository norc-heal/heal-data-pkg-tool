schema_experiment_tracker = {
    "type": "object",
    "description": "HEAL DSC Core Metadata piece to track and provide basic information about experiment(s) you will perform as part of your HEAL study. Clinical studies will often have only one experiment to report, while basic science studies often have several experiments that are grouped together under a single study.",
    "title": "HEAL Experiment Tracker",
    "properties": {
        "experimentId": {
            "title": "Experiment ID",
            "description": "id assigned to each experiment relevant to the data package; prefix is 'exp-' followed by a number starting with 1 for the first experiment, and iterating by 1 for each successive experiment (i.e. exp-1, exp-2, etc.)",
            "type": "string",
            "pattern": "^exp-+-*[0-9]*[1-9][0-9]*$",
            "priority": "all, high, auto"
        },
        "experimentType": {
            "title" : "Experiment Type",
            "description": "discovery|materials and methods development",
            "type": "string",
            "enum": ["discovery","materials and methods development"],
            "priority": "all"
        },
        "experimentDescription": {
            "title": "Experiment Description",
            "description": "provide a brief description of the experiment; this is NOT a protocol",
            "type": "string",
            "priority": "all, high"
        },
        "experimentQuestion": {
            "title": "Experiment Question(s)",
            "description": "what question(s) does the experimentalist hope to address with this experiment? be as specific as possible",
            "type": "array",
            "items": {
                "type": "string"
            },
            "priority": "all, high"
        },
        "experimentHypothesis": {
            "title": "Experiment Hypothesis(es)",
            "description": "for each question the experimentalist hopes to address with this experiment, what does the experimentalist hypothesize will be the result(s) of the experiment? Be as specific as possible",
            "type": "array",
            "items": {
                "type": "string"
            },
            "priority": "all"
        }
    }
}