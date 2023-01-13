import os
import webbrowser

entry_point = "main.py"

os.environ["FLASK_APP"] = entry_point
os.environ["FLASK_DEBUG"] = "1"

os.system("flask run --host=0.0.0.0")