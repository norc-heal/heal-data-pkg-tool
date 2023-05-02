import sys
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
        
        # add form and save button
        layout.addWidget(self.form)
        layout.addWidget(self.buttonSaveExp)

        #self.form.widget.on_changed.connect(self.validate_exp_id)
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out.txt','w')))
        #form.widget.on_changed.connect(lambda d: print(loads(dumps(d, indent=4))['experiment.id']))
        
        #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))

            
    def save_exp(self):
        #self.form.widget(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))
        print(self.form.widget.state)
        exp = self.form.widget.state
        print(exp["experiment.id"])
        print(dumps(exp, indent=4), file=open('exp-trk-'+ exp["experiment.id"] + '.txt','w'))
        #print(self.form[0])
        #print(qt_object_properties(self.form))

        #for widget in self.form:
        #    print(widget)

if __name__ == "__main__":
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = AnnotateExpWindow()
    window.show()
    sys.exit(app.exec_())