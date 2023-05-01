import sys
from json import dumps, loads

from qtpy import QtWidgets

from qt_jsonschema_form import WidgetBuilder

from schema_experiment_tracker import schema_experiment_tracker
import pandas as pd

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

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

    
    form = builder.create_form(schema, ui_schema)
    form.widget.state = {
        "experiment.id": "exp-1",
        #"schema_path": "some_file.py",
        #"integerRangeSteps": 60,
        #"sky_colour": "#8f5902"
    }
    form.show()

    #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))
    #form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out.txt','w')))
    #form.widget.on_changed.connect(lambda d: print(loads(dumps(d, indent=4))['experiment.id']))
    form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4), file=open('test-out-'+ loads(dumps(d, indent=4))['experiment.id'] + '.txt','w')))

    app.exec_()