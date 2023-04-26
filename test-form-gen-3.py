import sys
from json import dumps

from PyQt5 import QtWidgets

from pyqtschema.builder import WidgetBuilder

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    schema = {
        "type": "object",
        "title": "HEAL Experiment Tracker",
        "properties": {
            "experiment.id": {
                "label": "Experiment ID",
                "description": "id assigned to each experiment relevant to the data package; prefix is 'exp-' followed by a number starting with 1 for the first experiment, and iterating by 1 for each successive experiment (i.e. exp-1, exp-2, etc.)",
                "type": "string",
                "pattern": "^exp-+-*[0-9]*[1-9][0-9]*$"
            },
            "experiment.type": {
                "label" : "Experiment Type",
                "description": "discovery|materials and methods development",
                "type": "string",
                "enum": ["discovery","materials and methods development"]
            },
            "experiment.question": {
                "label": "Experiment Question(s)",
                "description": "what question(s) does the experimentalist hope to address with this experiment? be as specific as possible",
                "type": "string"
            },
            "experiment.description": {
                "label": "Experiment Description",
                "description": "provide a brief description of the experiment; this is NOT a protocol",
                "type": "string"
            },
            "experiment.hypothesis": {
                "label": "Experiment Hypothesis(es)",
                "description": "for each question the experimentalist hopes to address with this experiment, what does the experimentalist hypothesize will be the result(s) of the experiment? Be as specific as possible",
                "type": "string"
            }
        }
    }

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

    app.exec_()