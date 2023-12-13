import os
import pandas as pd

#需要把文件改成编码的格式（可以自己随时修改）
coding = 'utf-8'
# 文件夹目录（可以更改文件编码的文件夹~）
file_dir = 'F:\data_b'

import codecs

def handleEncoding(file_list):
    for original_file in file_list:
        f = open(original_file, 'rb+')
        content = f.read()  # 读取文件内容，content为bytes类型，而非string类型
        source_encoding = 'utf-8'
        # for root, dirs, files in os.walk(file_dir, topdown=False):
        #     for i in files:
        #         files_name = os.path.join(root, i)

        try:
            content.decode('utf-8').encode('utf-8')
            source_encoding = 'utf-8'
        except:
            try:
                content.decode('gbk').encode('utf-8')
                source_encoding = 'gbk'
            except:
                try:
                    content.decode('gb2312').encode('utf-8')
                    source_encoding = 'gb2312'
                except:
                    try:
                        content.decode('gb18030').encode('utf-8')
                        source_encoding = 'gb18030'
                    except:
                        try:
                            content.decode('big5').encode('utf-8')
                            source_encoding = 'gb18030'
                        except:
                            content.decode('cp936').encode('utf-8')
                            source_encoding = 'cp936'
        f.close()
    #####按照确定的encoding读取文件内容，并另存为utf-8编码：
        block_size = 4096
        with codecs.open(original_file, 'r', source_encoding) as f:
            newfile = original_file[:-4] + '_changeType.csv'
            with codecs.open(newfile, 'w', 'utf-8') as f2:
                while True:
                    content = f.read(block_size)
                    if not content:
                        break
                    f2.write(content)
        os.remove(original_file)

def run_coding():
    file_list = []
    for root, dirs, files in os.walk(file_dir, topdown=False):
        for i in files:
            files_name = os.path.join(root, i)
            file_list.append(files_name)
    return file_list
            # try:
            #     df1 = pd.read_csv(files_name, encoding='utf-8')
            # except:
            #     df1 = pd.read_csv(files_name, encoding='ANSI')
            # df1.to_csv(files_name, encoding=coding,index=None)

def clear(clear_path):
    # os.chdir(clear_path)                          # 文件夹所在路径                    【实际使用时需更改】
    # files = os.listdir( )
    # print('该文件夹内原文件分别为{}'.format(files),'\n')
    files = []
    for root, dirs, files in os.walk(file_dir, topdown=False):
        for i in files:
            files_name = os.path.join(root, i)
            files.append(files_name)
    for file in files:
        try:
            if "_changeType.csv" not in file:                               # 需要保留指定的对立面，即批量删除其对立面的       【实际使用时需更改】
                # print(file)                                      # 打印出特定类型之外的文件，即要删除的对象。这样的操作等价于保留指定类型的文件
                os.remove(file)                                  # 批量删除特定类型文件的核心命令，确定后再操作
        except:
            pass

if __name__ == '__main__':
    file_list = run_coding()
    handleEncoding(file_list)
    # clear('F:\data_b\财经')