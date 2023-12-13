import json
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from keras.models import Model
from keras.optimizers import Adam
from keras.layers import Input, Dense
from att import Attention
from keras.layers import GRU, Bidirectional
from tqdm import tqdm
import matplotlib.pyplot as plt

from albert_zh.extract_feature import BertVector

# with open("./data/multi-classification-train.txt", "r", encoding="utf-8") as f:
#     train_content = [_.strip() for _ in f.readlines()]

with open("C:\\Users\\Dell\\Desktop\\train.txt","r", encoding="utf-8") as f:
    train_content = [_.strip() for _ in f.readlines()]

with open("C:\\Users\\Dell\\Desktop\\train_dev.txt", "r", encoding="utf-8") as f:
    test_content = [_.strip() for _ in f.readlines()]

# 获取训练集合、测试集的事件类型
movie_genres = []

# 对字符串进行分片，获取事件类型
for line in train_content+test_content:
    genres = line.split(" ", maxsplit=1)[0].split("|")
    movie_genres.append(genres)

# 利用sklearn中的MultiLabelBinarizer进行多标签编码
mlb = MultiLabelBinarizer()
# 直接用fit函数，统计label种类
mlb.fit(movie_genres)

print("一共有%d种情感类型。" % len(mlb.classes_))

with open("event_type.json", "w", encoding="utf-8") as h:
    h.write(json.dumps(mlb.classes_.tolist(), ensure_ascii=False, indent=4))

# 对训练集和测试集的数据进行多标签编码
y_train = []
y_test = []

for line in train_content:
    genres = line.split(" ", maxsplit=1)[0].split("|")
    y_train.append(mlb.transform([genres])[0])

for line in test_content:
    genres = line.split(" ", maxsplit=1)[0].split("|")
    y_test.append(mlb.transform([genres])[0])

y_train = np.array(y_train)
y_test = np.array(y_test)

print(y_train.shape)
print(y_test.shape)

# 利用ALBERT对x值（文本）进行编码
# 最大句子长度为200
bert_model = BertVector(pooling_strategy="NONE", max_seq_len=200)
print('begin encoding')
# 把文本编码成albert向量
f = lambda text: bert_model.encode([text])["encodes"][0]

x_train = []
x_test = []

# 在 Python 长循环中添加一个进度提示信息
process_bar = tqdm(train_content)

for ch, line in zip(process_bar, train_content):
    movie_intro = line.split(" ", maxsplit=1)[1]
    # 把内容转换成向量
    x_train.append(f(movie_intro))

process_bar = tqdm(test_content)

for ch, line in zip(process_bar, test_content):
    movie_intro = line.split(" ", maxsplit=1)[1]
    x_test.append(f(movie_intro))

x_train = np.array(x_train)
x_test = np.array(x_test)

print("end encoding")
print(x_train.shape)


# 深度学习模型
# 模型结构：ALBERT + 双向GRU + Attention + FC
inputs = Input(shape=(200, 312, ), name="input")
# 训练一个双向的GRU
# 该层输入单元的 dropout 比率为0.2，所有中间层返回完整的输出序列
gru = Bidirectional(GRU(128, dropout=0.2, return_sequences=True), name="bi-gru")(inputs)
attention = Attention(32, name="attention")(gru)
num_class = len(mlb.classes_)
output = Dense(num_class, activation='sigmoid', name="dense")(attention)
model = Model(inputs, output)

# 模型可视化
# from keras.utils import plot_model
# plot_model(model, to_file='multi-label-model.png', show_shapes=True)
from keras import backend as K

def f1(y_true, y_pred):
    def recall(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())

        return recall

    def precision(y_true, y_pred):
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())

        return precision
    
    _y_true = K.gather(y_true, [0, 1, 2, 3, 4, 6])
    _y_pred = K.gather(y_pred, [0, 1, 2, 3, 4, 6])

    precision = precision(_y_true, _y_pred)
    recall = recall(_y_true, _y_pred)

    return 2*((precision*recall)/(precision+recall+K.epsilon()))



model.compile(loss='binary_crossentropy',
              optimizer=Adam(),
              metrics=[f1])

history = model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=128, epochs=10)
model.save('event_type.h5')


# 训练结果可视化
# 绘制loss和acc图像
plt.subplot(2, 1, 1)
epochs = len(history.history['loss'])
plt.plot(range(epochs), history.history['loss'], label='loss')
plt.plot(range(epochs), history.history['val_loss'], label='val_loss')
plt.legend()

plt.subplot(2, 1, 2)
epochs = len(history.history['f1'])
plt.plot(range(epochs), history.history['f1'], label='f1')
plt.plot(range(epochs), history.history['val_f1'], label='val_f1')
plt.legend()
plt.savefig("loss_f1.png")
