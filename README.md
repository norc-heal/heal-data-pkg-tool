# heal-dsc-gui-dev
development of a desktop app that implements cli tools for data packaging and curation compliant with nih heal initiative data packaging recommendations; developed by heal data sharing consultancy team at norc at the university of chicago

# python virtual environment for development
install:
- healdata_utils (from github)
    - this will install many dependencies required for dev of this application as well, including frictionless, pandas, etc.
- PyQt5
- PyInstaller
- pipe

# to create application executable (Windows)
- ensure application is working locally first
- open cmd
- activate development python virtual environment

```
$ call C:\Users\tentner-andrea\Envs\newer-gui-env\Scripts\activate
``` 

- navigate to folder with main application script (dsc_pkg_tool.py)
- start in de-bugging mode (retain the console output and get at least imports debug reports as imports are a common point of failure):  

```
$ pyinstaller --name "dscPkgTool" --icon=heal-icon.ico --add-data="heal-icon.ico;." --add-data="resources;resources" --collect-data frictionless --collect-all pipe --hidden-import pipe –hidden-import frictionless.plugins –hidden-import frictionless.plugins.remote –hidden-import pyreadstat._readstat_writer –hidden-import pyreadstat.worker --paths=C:\Users\tentner-andrea\Envs\newer-gui-env\Lib\site-packages\ --paths=C:\Users\tentner-andrea\project-repositories\dsc\heal-dsc-gui-dev\ --debug=imports dsc_pkg_tool.py
```

- then call the resulting executable from cmd like:

```
$ dist\dscPkgTool\dscPkgTool.exe
```

- if the application fails to launch check the console for point of failure to start debugging
- once you've got the application launching properly from cmd, re-make the application in "no console" mode for distribution by repeating the pyinstaller command above, but adding --noconsole
- confirm that the application launches when you double click on the executable and run through any testing protocols prior to distributing
