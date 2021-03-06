from flask import Flask, request, jsonify, make_response
import logging
import requests
import markdown
import time
import os
import threading

app = Flask(__name__)
logtime = time.strftime("%Y-%m-%d", time.localtime()) 
logging.basicConfig(filename=f"/var/www/class-register/logs/{logtime}.log",format='[%(asctime)s] [%(filename)s] [line:%(lineno)d] [In %(funcName)s] %(levelname)s %(message)s', level=logging.INFO)

logging.info("Starting server!")
from api_2_1_0 import api as api_2_1_0_blueprint
app.register_blueprint(api_2_1_0_blueprint, url_prefix='/api/v2.1.0')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal error, please contact with the developer!'}), 500)

@app.route('/log', methods=['GET'])
def log():
    with open(f"/var/www/class-register/logs/{logtime}.log", "r") as f:

        texts = f.read()
        text = texts.replace("\n", "\n\n")

        html = markdown.markdown(text)
    return html

if __name__ == '__main__':
    # threading.Thread(target=ClearLogs).start()
    app.run(threaded=True)