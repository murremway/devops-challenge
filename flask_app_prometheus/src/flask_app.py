from flask import Flask, Response
from helpers.middleware import setup_metrics
import prometheus_client

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')


app = Flask(__name__)
setup_metrics(app)

@app.route('/ping/')
def test():
    return 'pong'

@app.route('/ping1/')
def test1():
    1/0
    return 'pong'

@app.errorhandler(500)
def handle_500(error):
    return str(error), 500

@app.route('/metrics')
def metrics():
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run()
