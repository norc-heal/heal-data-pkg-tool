import sys
from json import dumps, dump

from PyQt5 import QtWidgets

from pyqtschema.builder import WidgetBuilder

from schema_experiment_tracker import schema_experiment_tracker
import pandas as pd

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

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

    builder = WidgetBuilder(schema)
    form = builder.create_form(ui_schema)
    form.widget.state = {
        "experiment.id": "exp-1",
        #"schema_path": "some_file.py",
        #"integerRangeSteps": 60,
        #"sky_colour": "#8f5902"
    }
    form.show()
    form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))
    #form.widget.on_changed.connect(lambda d: dumps(d, indent=4))

    app.exec_()