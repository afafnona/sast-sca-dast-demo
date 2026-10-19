import os, subprocess
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)
# Secret comes from the environment, never hardcoded
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

ALLOWED = {"ls": ["ls", "-l"], "date": ["date"], "whoami": ["whoami"]}

@app.route('/hello')
def hello():
    name = escape(request.args.get('name', 'Guest'))   # fixes XSS
    return f"<h1>Hello Page</h1><p>Hello, {name}!</p><p><a href='/'>Back</a></p>"

@app.route('/execute')
def execute():
    key = request.args.get('cmd', 'ls')
    if key not in ALLOWED:                              # fixes command injection
        return "Command not allowed", 400
    result = subprocess.run(ALLOWED[key], capture_output=True, text=True)
    return f"<h1>Execute</h1><pre>{escape(result.stdout)}</pre><p><a href='/'>Back</a></p>"

@app.route('/admin')
def admin():
    return "<h1>Admin Area</h1><p><a href='/'>Back</a></p>"   # no secret displayed

@app.after_request
def security_headers(resp):                             # clears most ZAP Medium/Low alerts
    resp.headers['Content-Security-Policy'] = "default-src 'self'"
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['Permissions-Policy'] = 'geolocation=()'
    return resp

if __name__ == '__main__':
    app.run(debug=False, host=os.environ.get('HOST', '127.0.0.1'))
