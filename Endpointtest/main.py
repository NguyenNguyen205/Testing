from flask import Flask, Response
# from flask_ngrok import run_with_ngrok
from flask_cors import CORS
# from flask_lt import run_with_lt
app = Flask('Testing')
CORS(app)
# run_with_ngrok(app)
# run_with_lt(app)
@app.route('/')
def home():
  res = Response("Hello world again")
  return res;

app.run()
