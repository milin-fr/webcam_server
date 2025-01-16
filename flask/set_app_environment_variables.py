import os

def set_app_environment_variables(app):
    allowed_environment_values = ["development", "production"]

    if os.path.isdir("flask/virtual_env"):  # this is a hack to avoid importing pip install python-dotenv in production
        from dotenv import load_dotenv
        load_dotenv()

    app.global_variables["debug"] = True if int(os.environ.get("display_debug")) == 1 else False
    app.global_variables["environment"] = os.environ["environment"] if os.environ["environment"] in allowed_environment_values else "development"


    app.global_variables["server_port"] = os.environ["server_port"]
    app.global_variables["redis_url"] = os.environ.get("redis_url")
