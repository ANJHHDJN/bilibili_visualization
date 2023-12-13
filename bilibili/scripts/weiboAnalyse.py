import pandas as pd
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType
from pyecharts import options as opts
from operator import itemgetter, attrgetter

def weiboWordcloud(percent = 0)-> WordCloud:
# percent=2
    classes = {'0':'校园学习', '1':'社科人文','2': '科学科普','3': '职业职场','4': '财经', '5':'野生技术协会'}
    file = classes[str(percent)]+'词频表.csv' 
    print(file)
    data = pd.read_csv('词频表(去单字)/' + file, encoding='gb18030')
    word = [i[0] for i in data[['词语']].values]
    value_time = [i[0] for i in data[['次数']].values]
    value_time = list(map(int, value_time))
    word_tulpe = list(zip(word, value_time))
    word_tulpe = sorted(word_tulpe, key=itemgetter(1), reverse=True)[:500]
    # word_tulpe = [('和', 2), ('好', 5), ('了', 3)]
    print(word_tulpe)

    c = (
        WordCloud()
        .add("", word_tulpe,word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title=classes[str(percent)] + '词云图'))
    )
    return c