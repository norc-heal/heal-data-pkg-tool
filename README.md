# HEAL Data Package Tool
Desktop tool that provides a user-friendly tool/interface to operationalize data packaging and curation compliant with NIH HEAL initiative data packaging recommendations; Developed by HEAL Data Sharing Consultancy (DSC) team at NORC at the University of Chicago.

**Enables:**
- Create/initialize data package
- Create and complete standard data package metadata files
    - Study level
      - experiment-tracker - one per study
      - resource-tracker - one per study
    - File level
      - results-tracker - one per multi-result file (e.g. manuscript)
      - data-dictionary - one per tabular data file

# Download and Open Tool (Windows executable)
- Go to [latest release](https://github.com/norc-heal/heal-data-pkg-tool/releases/latest/) for tool repository 
- Expand release assets
- Download dsc-pkg-tool-windows.zip
- Unzip archive
- Double click on dsc-pkg-tool-windows\dsc_pkg_tool\dsc_pkg_tool.exe to open tool

# Download and Open Tool (Mac executable)
- Signing and notarizing procedures under development - we hope to have this up by mid October 2023
- In the meantime, for Mac users with some familiarity with Python and the command line, you can follow [these instructions](https://norc-heal.github.io/heal-data-pkg-tool-docs/about/download/start-mac/) to run the tool locally 

# (Developers only) Python virtual environment for development
install:
``` pip install -r requirements.txt ```







