from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import babel
from set_app_environment_variables import set_app_environment_variables

app = Flask(__name__, static_folder='static')
app.global_variables = {}
set_app_environment_variables(app)

app.config['SQLALCHEMY_BINDS'] = {
    "people_counter_database": {
        "url": "sqlite:///people_counter_database.db",
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = False


db = SQLAlchemy(app)

@app.template_filter()
def format_datetime(data, format="datetime"):
    date = tools.to_datetime(data)
    if format == "date":
        format = "dd/MM/yyyy"
    elif format == "time":
        format = "HH:mm:ss"
    elif format == "full":
        return babel.dates.format_datetime(date, locale="fr_FR")
    else:
        format = "dd/MM/yyyy 'à' HH:mm:ss"
    return babel.dates.format_datetime(date, format)

from routes.web import *
from routes.api import *

if __name__ == "__main__":
    app.run(debug=app.global_variables["debug"], host="0.0.0.0", port=app.global_variables["server_port"])
