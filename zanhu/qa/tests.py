from flask import Flask, request

app = Flask(__name__)


@app.route("/phoneLog_callback/", methods=["GET", "POST"])
def phoneLog_callback():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    return 'Hello World!'


@app.route("/task_callback/", methods=["GET", "POST"])
def task_callback():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    return 'Hello task!'


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
