from flask import Flask, Blueprint, url_for, redirect,  render_template, request, session

app = Flask(__name__)

from pydoku import py_api

app.register_blueprint(py_api)

@app.route('/')
def init():
	return render_template('pydoku.html')

if __name__ == "__main__":
	app.run()

