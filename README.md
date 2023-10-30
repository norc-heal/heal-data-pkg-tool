# HEAL Data Packaging Tool
Desktop tool that provides a user-friendly tool/interface to operationalize data packaging and curation compliant with NIH HEAL initiative data packaging recommendations; Developed by HEAL Data Sharing Consultancy (DSC) team at NORC at the University of Chicago.

## **Tool Functions**
- Create/initialize data package
- Create and complete standard data package metadata files, including
    - Study level
      - Experiment-tracker - one per study
      - Resource-tracker - one per study
    - File level
      - Results-tracker - one per multi-result file (e.g. manuscript)
      - Data-dictionary - one per tabular data file
     
## **Tool Documentation**
- Navigate to the [HEAL Data Packaging Tool Documentation](https://norc-heal.github.io/heal-data-pkg-tool-docs/) website for instructions on:
    - How to Download and Open the Tool
        - Instructions for how to download and open the tool can also be found just below
    - How to Use the Tool 

# Download and Open Tool (Windows executable)
- Go to the download [link](https://github.com/norc-heal/heal-data-pkg-tool/releases/latest/) for the latest release of the tool  
- Expand "Assets"
- Download the asset: dsc-pkg-tool-windows.zip
- Unzip archive
- The result will be a directory called dsc-pkg-tool-windows with a single file called dsc_pkg_tool.exe inside. Double click this executable file to open tool.  
- **NOTE**:
    - **Delete previous version(s) of the tool**: If you have downloaded a previous version of the tool, delete the previous version of the tool (dsc-pkg-tool-windows\dsc_pkg_tool.exe – delete the dsc-pkg-tool-widows folder) prior to downloading and unzipping the current version of the tool, as having more than one version of the tool in the same file location may lead to problems with duplicate file names.
    - **DO NOT delete your dsc-pkg folder or contents**: If you have already used the tool to create/initialize your data package (i.e. created your dsc-pkg folder within your study folder), **DO NOT** delete your dsc-pkg folder or any of its contents (i.e. standard data package metadata files such as experiment, resource, and results trackers and data dictionaries)

# Download and Open Tool (Mac executable)
- Go to the download [link](https://github.com/norc-heal/heal-data-pkg-tool/releases/latest/) for the latest release of the tool  
- Expand "Assets"
- Download the asset: dsc-pkg-tool-mac.zip
- Unzip archive
- The result will be a directory called dsc-pkg-tool-mac with a single file called dsc_pkg_tool inside. Right click on the dsc_pkg_tool file and select “Open.” <i><b>Note:</b> You will receive a pop-up window with a notification that macOS cannot verify the developer. You will need to select “Open” within this pop-up window up to override and open the app.</i>  
- **NOTE**:
    - **DO NOT delete your dsc-pkg folder or contents**: If you have already used the tool to create/initialize your data package (i.e. created your dsc-pkg folder within your study folder), **DO NOT** delete your dsc-pkg folder or any of its contents (i.e. standard data package metadata files such as experiment, resource, and results trackers and data dictionaries) 

# (Developers only) Python virtual environment for development
install:
``` pip install -r requirements.txt ```







