from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    with pull_session(url="http://localhost:5006/") as session:
        script = server_session(session_id=session.id, url='http://localhost:5006')
    return render_template("index.html", script=script, template="Flask")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
