from random import randrange

from flask.json import jsonify
from flask import Flask, render_template
from flask import request

import pandas as pd

from pyecharts import options as opts
from pyecharts.charts import Line

from scripts.jiebafenci import render_wordcloud
from scripts.weiboAnalyse import weiboWordcloud

from multi_label_classification.model_predict import predict

app = Flask(__name__, static_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Histogram")
def document():
    return render_template("Histogram.html")


@app.route("/sentiment")
def nlpNotebook():
    return render_template("sentiment.html")


@app.route("/predict")
def anaNotebook():
    return render_template("predict.html")


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        text = result['Text']
        sentiment = predict(text)
        return render_template("result.html", text=sentiment)


@app.route("/wordcloud", methods=['POST', 'GET'])
def get_word_chart():
    if request.method == 'GET':
        i = request.args.get('value', '')
        if not i:
            i = 0
        print(i)
        return render_wordcloud(i).dump_options_with_quotes()


@app.route("/weiboCloud", methods=['POST', 'GET'])
def get_weibo_chart():
    if request.method == 'GET':
        i = request.args.get('value', '')
        if not i:
            i = 0
        print(i)
        return weiboWordcloud(i).dump_options_with_quotes()


if __name__ == "__main__":
    app.run()