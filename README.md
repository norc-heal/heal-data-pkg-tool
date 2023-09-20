# HEAL Data Package Tool
Desktop tool that provides a user-friendly tool/interface to operationalize data packaging and curation compliant with NIH HEAL initiative data packaging recommendations; Developed by HEAL Data Sharing Consultancy (DSC) team at NORC at the University of Chicago.

**Enables:**
- Create/initialize data package
- Create and complete standard data package metadata files, including
    - Study level
      - Experiment-tracker - one per study
      - Resource-tracker - one per study
    - File level
      - Results-tracker - one per multi-result file (e.g. manuscript)
      - Data-dictionary - one per tabular data file

# Download and Open Tool (Windows executable)
- Go to [latest release](https://github.com/norc-heal/heal-data-pkg-tool/releases/latest/) for tool repository 
- Expand release assets
- Download dsc-pkg-tool-windows.zip
- Unzip archive
- Double click on dsc-pkg-tool-windows\dsc_pkg_tool\dsc_pkg_tool.exe to open tool - **NOTE**: Do not move the dsc_pkg_tool.exe file from its location within the dsc-pkg-tool-windows\dsc_pkg_tool\ folder - the executable requires the other contents contained within the folder to function. 
- **NOTE**:
    - **Delete previous version(s) of the tool**: If you have downloaded a previous version of the tool, delete the previous version of the tool (dsc-pkg-tool-windows\dsc_pkg_tool\ folder) prior to downloading and unzipping the current version of the tool, as having more than one version of the tool in the same file location may lead to problems with duplicate file names.
    - **DO NOT delete your dsc-pkg folder or contents**: If you have already used the tool to create/initialize your data package (i.e. created your dsc-pkg folder within your study folder), **DO NOT** delete your dsc-pkg folder or any of its contents (i.e. standard data package metadata files such as experiment, resource, and results trackers and data dictionaries)

# Download and Open Tool (Mac executable)
- Signing and notarizing procedures under development - we hope to have this up by mid October 2023
- In the meantime, for Mac users with some familiarity with Python and the command line, you can follow [these instructions](https://norc-heal.github.io/heal-data-pkg-tool-docs/about/download/start-mac/) to run the tool locally 

# (Developers only) Python virtual environment for development
install:
``` pip install -r requirements.txt ```







