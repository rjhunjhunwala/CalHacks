from flask import Flask

app = Flask(__name__)


@app.route('/<id>')
def hello_world(id):



if __name__ == '__main__':
    app.run()
