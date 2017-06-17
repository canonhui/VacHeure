#!/usr/bin/env python3
from app import app
app.run(debug=True)
#from werkzeug.serving import run_simple
#run_simple('localhost', 5000, app, use_debugger=True)