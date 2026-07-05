from flask import Flask, jsonify
from auth import auth
from database import init_db
from tasks import tasks


app = Flask(__name__)

app.register_blueprint(auth)
app.register_blueprint(tasks)

init_db()

@app.route("/")
def welcome():
    return "Welcome To My First Project"

if __name__ == "__main__":
    app.run(debug=True)