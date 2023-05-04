import sys
import os
from json import dumps, loads

from qtpy import QtWidgets

from qt_jsonschema_form import WidgetBuilder

from schema_experiment_tracker import schema_experiment_tracker
from dsc_pkg_utils import qt_object_properties
import pandas as pd

class AnnotateExpWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Annotate Experiment")
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # Create the form widget 
        builder = WidgetBuilder()

        schema = schema_experiment_tracker
        ui_schema = {}

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
            "experiment.id": "exp-1",
            #"schema_path": "some_file.py",
            #"integerRangeSteps": 60,
            #"sky_colour": "#8f5902"
        }
        #form.show()

        # create save button
        self.buttonSaveExp = QtWidgets.QPushButton(text="Save experiment",parent=self)
        self.buttonSaveExp.clicked.connect(self.save_exp)

        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        # add form and save button and status message box
        layout.addWidget(self.form)
        layout.addWidget(self.buttonSaveExp)
        layout.addWidget(self.userMessageBox)

        #self.form.widget.on_changed.connect(self.validate_exp_id)
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out.txt','w')))
        #form.widget.on_changed.connect(lambda d: print(loads(dumps(d, indent=4))['experiment.id']))
        
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))

            
    def save_exp(self):
        #self.form.widget(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))
        print(self.form.widget.state)
        exp = self.form.widget.state
        exp_id = exp["experiment.id"]
        print(exp_id)

        saveFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your DSC Data Package Directory - Your new experiment will be saved there!')
        
        expFileName = 'exp-trk-'+ exp_id + '.txt'
        saveFilePath = os.path.join(saveFolderPath,expFileName)
        
        messageText = ""
        
        if os.path.isfile(saveFilePath):
            messageText = "An experiment file for an experiment with id " + exp_id + " already exists at " + saveFilePath + ". You may want to do one or both of: 1) Use the View/Edit tab to view your experiment tracker file and check which experiment IDs you've already used and added to your tracker, 2) Use File Explorer to navigate to your DSC Data Package Directory and check which experiment IDs you've already used and for which you've already created experiment files - these files will be called \'exp-trk-exp-{a number}.txt\'. While you perform these checks, your experiment tracker form will remain open unless you explicitly close it. You can come back to it, change your experiment ID, and hit the save button again to save with an experiment ID that is not already in use. If you meant to overwrite an experiment file you previously created for an experiment with this experiment ID, please delete the previously created experiment file and try saving again." 
        else:
            f=open(saveFilePath,'w')
            print(dumps(exp, indent=4), file=f)
            f.close()
            messageText = "Your experiment file was successfully written at: " + saveFilePath + ". You'll want to head back to the \'Add Experiment\' tab and use the \'Add Experiment\' button to add this experiment file to your experiment tracker file! You can do this now, or later - You can add experiment files to the experiment tracker file one at a time, or you can add multiple experiment files all at once, so you may choose to create experiment files for all of your experiments and then add them in one go to your experiment tracker file."
        
        self.userMessageBox.setText(messageText)
        
        

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = AnnotateExpWindow()
    window.show()
    sys.exit(app.exec_())