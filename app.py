from flask import Flask, render_template, url_for, request, redirect, send_file, session
import os
from random import choice
# import flask_login
# import termcolor
import json

from sqlalchemy import null
from feature_extractor import get_features
from predictor import keras_predict
import pandas as pd
from extract import extract_features


app = Flask(__name__)
app.secret_key = '215729847238472749172546259184120'


@app.route('/prediction/', methods=['GET', 'POST'])
@app.route('/predicion/<string:descr>,<string:munic>,<string:prov>,<int:pred>/', methods=['GET', 'POST'])
def predict(prov, munic, descr, pred):
    ifeats = pd.DataFrame(get_features(descr), index=[0])
    feats = extract_features(descr, prov, munic)

    to_delete = []
    lfeats = []
    num = False

    for index, row in ifeats.iterrows():
        for tag, el in row.iteritems():
            if(tag == "cuartos"):
                num = True
            if el == -1 or el == False:
                to_delete.append(tag)
            else:
                if(tag == "banos"):
                    tag = "baños"
                if(tag == "escuela"):
                    tag = "escuela cercana"
                if(tag == "hospital"):
                    tag = "hospital cercano"
                tag = tag.capitalize()
                if(num):
                    lfeats.append((tag, el))
                elif(el == 0):
                    lfeats.append((tag, "no"))
                else:
                    lfeats.append((tag, "sí"))

    ifeats = ifeats.drop(to_delete, axis=1)

    # print(termcolor.colored(feats,'blue'))
    pred = int(keras_predict(feats))
    return render_template("prediction.html", descr=descr, munic=munic, prov=prov, features=lfeats, pred=pred)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":

        print('posting')
        prov = request.form['provincia']
        munic = request.form['municipio']
        descr = request.form['descripcion']
        # print(termcolor.colored(f"Tried to predict: {descr}", color="magenta"))
        ans = 10000
        return redirect(url_for('predict', prov=prov, munic=munic, descr=descr, pred=ans))
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
