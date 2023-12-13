import json
import numpy as np
from keras.models import load_model

# -*- coding: utf-8 -*-
from keras import backend as K
from keras.engine.topology import Layer

import sys
# sys.path.append(r"bili/multi_label_classification")
sys.path.append(r'F:\bili csv\bili\multi_label_classification')

from att import Attention

from albert_zh.extract_feature import BertVector
from keras import backend as K


def f1(y_true, y_pred):
    def recall(y_true, y_pred):
        """Recall metric.



        Only computes a batch-wise average of recall.



        Computes the recall, a metric for multi-label classification of

        how many relevant items are selected.

        """

        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))

        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))

        recall = true_positives / (possible_positives + K.epsilon())

        return recall

    def precision(y_true, y_pred):
        """Precision metric.



        Only computes a batch-wise average of precision.



        Computes the precision, a metric for multi-label classification of

        how many selected items are relevant.

        """

        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))

        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))

        precision = true_positives / (predicted_positives + K.epsilon())

        return precision

    _y_true = K.gather(y_true, [0, 1, 2, 3, 4, 6])

    _y_pred = K.gather(y_pred, [0, 1, 2, 3, 4, 6])

    precision = precision(_y_true, _y_pred)

    recall = recall(_y_true, _y_pred)

    return 2 * ((precision * recall) / (precision + recall + K.epsilon()))


def predict(text):
    model = load_model(r"F:\bili csv\bili\multi_label_classification\event_type.h5",
                       custom_objects={
                           "Attention": Attention,
                           "f1": f1
                       })

    labels = []

    bert_model = BertVector(pooling_strategy="NONE", max_seq_len=200)

    # 将句子转换成向量
    vec = bert_model.encode([text])["encodes"][0]
    x_train = np.array([vec])

    # 模型预测
    predicted = model.predict(x_train)[0]

    indices = [i for i in range(len(predicted)) if predicted[i] > 0.55]

    with open(r"F:\bili csv\bili\multi_label_classification\event_type.json",
              "r",
              encoding="utf-8") as g:
        movie_genres = json.loads(g.read())

    result = "|".join([movie_genres[index] for index in indices])
    print(result)

    return result


if __name__ == "__main__":
    predict('1')

# load_model = load_model(r"C:\Users\dell\Desktop\multi-label-classification-4-event-type-master\event_type.h5", custom_objects={"Attention": Attention,"f1": f1})

# # text = "也就只有中国在这种时候能体现大国应有的风范。以大局为重，欧美那些国家？什么玩意儿？。不过重点是，咱们医护人员确实很累了。"

# labels = []

# bert_model = BertVector(pooling_strategy="NONE", max_seq_len=200)

# # 将句子转换成向量
# vec = bert_model.encode([text])["encodes"][0]
# x_train = np.array([vec])

# # 模型预测
# predicted = load_model.predict(x_train)[0]

# indices = [i for i in range(len(predicted)) if predicted[i] > 0.55]

# with open(r"C:\Users\dell\Desktop\multi-label-classification-4-event-type-master\event_type.json", "r", encoding="utf-8") as g:
#     movie_genres = json.loads(g.read())

# # t2=open(r'C:\Users\dell\Desktop\t2.txt','w')
# # t1.close()
# # t2.close()

# result="|".join([movie_genres[index] for index in indices])
# print(result)

# file2=open(r'C:\Users\dell\Desktop\result.txt', 'w',encoding='utf-8')
# file2.write(result)

# file1.close()
# file2.close()
# # print("预测语句: %s" % text)
# # print("预测情感类型: %s" % "|".join([movie_genres[index] for index in indices]))
