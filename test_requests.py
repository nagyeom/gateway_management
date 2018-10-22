# -*- coding: utf-8 -*-

import requests
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    data = {}

    if request.method == 'POST':
        #data = json.load(request.data)
        print ('1')
        print (request.data)
    #return render_template('test_layout.html',data=data)
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=10002)