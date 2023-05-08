import sys
import os
from json import dumps, loads

from qtpy import QtWidgets

from qt_jsonschema_form import WidgetBuilder

from schema_resource_tracker import schema_resource_tracker
from dsc_pkg_utils import qt_object_properties
import pandas as pd

class AnnotateResourceWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annotate Resource")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # Create the form widget 
        builder = WidgetBuilder()

        schema = schema_resource_tracker
        ui_schema = {
            "path": {
                "ui:widget": "filepath"
            }
            ,
            "assoc.file.dd": {
                "ui:widget": "filepath"
            },
            "assoc.file.protocol": {
                "ui:widget": "filepath"
            },
            "assoc.file.id.map": {
                "ui:widget": "filepath"
            },
            "assoc.file.id.map": {
                "ui:widget": "filepath"
            }
        }

        #ui_schema = {
        #    "schema_path": {
        #        "ui:widget": "filepath"
        #    },
        #    "sky_colour": {
        #        "ui:widget": "colour"
        #    }
        #
        #}

        self.form = builder.create_form(schema, ui_schema)
        self.form.widget.state = {
            "exp.belongs.to": "exp-999",
            "access.date": "2099-01-01"
            #"schema_path": "some_file.py",
            #"integerRangeSteps": 60,
            #"sky_colour": "#8f5902"
        }
        #form.show()

        # create save button
        self.buttonSaveResource = QtWidgets.QPushButton(text="Save resource",parent=self)
        self.buttonSaveResource.clicked.connect(self.save_resource)

        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        # add form and save button and status message box
        layout.addWidget(self.form)
        layout.addWidget(self.buttonSaveResource)
        layout.addWidget(self.userMessageBox)

        #self.form.widget.on_changed.connect(self.validate_exp_id)
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out.txt','w')))
        #form.widget.on_changed.connect(lambda d: print(loads(dumps(d, indent=4))['experiment.id']))
        
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))

            
    def save_resource(self):
        #self.form.widget(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))
        print(self.form.widget.state)
        resource = self.form.widget.state
        resource_id = exp["resource.id"]
        print(resource_id)

        saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new resource will be saved there!')
        
        resourceFileName = 'resource-trk-'+ resource_id + '.txt'
        saveFilePath = os.path.join(saveFolderPath,resourceFileName)
        
        messageText = ""
        
        if os.path.isfile(saveFilePath):
            messageText = "A resource file for a resource with id " + resource_id + " already exists at " + saveFilePath + ". You may want to do one or both of: 1) Use the View/Edit tab to view your resource tracker file and check which resource IDs you've already used and added to your tracker, 2) Use File Explorer to navigate to your DSC Data Package Directory and check which resource IDs you've already used and for which you've already created resource files - these files will be called \'resource-trk-resource-{a number}.txt\'. While you perform these checks, your resource tracker form will remain open unless you explicitly close it. You can come back to it, change your resource ID, and hit the save button again to save with a resource ID that is not already in use. If you meant to overwrite a resource file you previously created for an resource with this resource ID, please delete the previously created resource file and try saving again." 
        else:
            f=open(saveFilePath,'w')
            print(dumps(resource, indent=4), file=f)
            f.close()
            messageText = "Your resource file was successfully written at: " + saveFilePath + ". You'll want to head back to the \'Add Resource\' tab and use the \'Add Resource\' button to add this resource file to your resource tracker file! You can do this now, or later - You can add resource files to the resource tracker file one at a time, or you can add multiple resource files all at once, so you may choose to create resource files for several/all of your resources and then add them in one go to your resource tracker file."
        
        self.userMessageBox.setText(messageText)
        
        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = AnnotateResourceWindow()
    window.show()
    sys.exit(app.exec_())