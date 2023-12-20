# HEAL Experiment Tracker

*HEAL DSC Core Metadata piece to track and provide basic information about experiment(s) you will perform as part of your HEAL study. Clinical studies will often have only one experiment to report, while basic science studies often have several experiments that are grouped together under a single study.*

## Properties

- **`experimentId`** *(string)*: ID assigned to each experiment relevant to the data package; prefix is 'exp-' followed by a number starting with 1 for the first experiment, and iterating by 1 for each successive experiment (i.e. exp-1, exp-2, etc.).
- **`experimentName`** *(string)*: If you may want to link specific study files or study results to a specific single study experiment or activity, it's a good idea to assign a human-recognizable "experiment name" to your study experiment or activity here. If you are using the DSC Data Packaging Tool, you will be able to select from a pick list of experiment names to make this link, which will be easier than linking by experiment ID. The Experiment Name should be short and descriptive, and must be unique. It is meant to be an alternative ID assigned to each experiment relevant to the data package that is human readable and recognizable as related to a specific study experiment or activity. In order to make this both human and machine readable, 1) name must start with a lower case letter, 2) name must end with a lower case letter or number, 3) only characters allowed are lower case letters, numbers, and hyphens (use hyphen instead of space), 4) name has a max length of 50, 5) name must be unique (append an iterable number as a suffix to make unique if necessary; e.g. "-1", "-2").
- **`experimentType`** *(string)*: discovery|materials and methods development. Must be one of: `["", "discovery", "materials and methods development"]`.
- **`experimentDescription`** *(string)*: provide a brief description of the experiment; this is NOT a protocol.
- **`experimentQuestion`** *(array)*: what question(s) does the experimentalist hope to address with this experiment? be as specific as possible.
  - **Items** *(string)*
- **`experimentHypothesis`** *(array)*: for each question the experimentalist hopes to address with this experiment, what does the experimentalist hypothesize will be the result(s) of the experiment? Be as specific as possible.
  - **Items** *(string)*
- **`annotationCreateDateTime`** *(string)*: Date time at which the experiment annotation file for the experiment was created; auto-inferred.
- **`annotationModDateTime`** *(string)*: Date time at which the experiment annotation file for the experiment was last modified; auto-inferred.

