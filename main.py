# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# pc_type           lenovo
# create_time:      2019/4/15 23:23
# file_name:        main.py
# github            https://github.com/inspurer
# qq邮箱            2391527690@qq.com


import pandas as pd
import os
from math import ceil

import jieba
from jieba import analyse

analyse.set_stop_words('StopWords.txt')

EXPORT_FILE_NAME = "【数据清洗后】.xlsx"

if not os.path.exists(EXPORT_FILE_NAME):
    ## 从 excel 中加载数据
    df1 = pd.read_excel("【历史文章】.xlsx")
    ## 截取指定的列
    data1 = df1[['标题', '点赞数', '阅读数']]
    df2 = pd.read_excel("【文章内容】.xlsx")
    data2 = df2[['标题', '文本内容', '文章链接']]
    # # 过滤掉文本内容里面的换行符
    # data2['文本内容'].apply(lambda text: text.replace('[\r\n]', ''))
    # print(dir(df1))
    # 内连接,合并 data1 和 data2 在“标题”上匹配的元组，不保留未匹配的元组
    data = pd.merge(data1, data2, how="inner", on="标题")
    # 将清洗过的数据输出到 excel 中, index = False 的目的是不再自动创建行索引
    data.to_excel(EXPORT_FILE_NAME, index=False)
    print(data)

else:
    data = pd.read_excel(EXPORT_FILE_NAME)
# print(data)

# 前 20% 阅读量的标题被定义为好标题
# 后 20% 阅读量的标题被定义为差标题
threshold = ceil(data.shape[0] * 0.2)
best_titles = data.nlargest(threshold,'阅读数')
worst_titles = data.nsmallest(threshold,'阅读数')
# df [[]] 获取 df, [] 获取 series
best_titles_text = "".join(best_titles['标题'].values.tolist())
worst_titles_text = "".join(worst_titles['标题'].values.tolist())

import matplotlib.pyplot as plt
from scipy.misc import imread
from wordcloud import WordCloud

def WordcloudingKeywordsOfText(text,export_filename):
    cut_words = jieba.lcut(text)
    with open(export_filename+".txt",'w',encoding='utf-8') as f:
        f.write("/".join(cut_words))
    WC = WordCloud(
        font_path='my_font.ttf',
        background_color="#ffffff",
        max_words=2000,
        mask=imread('wordcloud_back.png'),
        random_state=42
    )
    WC.generate("".join(jieba.lcut(text))
)
    plt.figure(export_filename)
    plt.imshow(WC)
    plt.axis("off")
    WC.to_file(export_filename+".png")
    ...
WordcloudingKeywordsOfText(best_titles_text,"好的标题")
WordcloudingKeywordsOfText(worst_titles_text,"差的标题")
import matplotlib
from scipy import optimize
import numpy as np

# 设置中文字体和负号正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
read_num = data['阅读数'].values.tolist()
praise_num = data['点赞数'].values.tolist()
plt.figure()
plt.xlabel('阅读数')
plt.ylabel('点赞数')
plt.title('点赞数和阅读数分布图')
plt.scatter(x=read_num,y=praise_num,label="实际值")

# def line_fit(x,A,B):
#     return A*x + B
#
# # 直线拟合与绘制
# A1, B1 = optimize.curve_fit(line_fit, read_num, praise_num)[0]
# x1 = np.arange(min(read_num), max(read_num), 1000)
# y1 = A1 * x1 + B1
from sklearn.linear_model import LinearRegression
from scipy import vectorize

lr = LinearRegression()
lr.fit(np.array(read_num).reshape(-1,1),praise_num)
x1 = np.array(read_num).reshape(-1,1)
y1 = lr.predict(x1)
# 对 np.array 每个元素取整操作，应用scipy.vectorize()函数
y1 = vectorize(lambda x:ceil(x))(y1)
plt.plot(x1,y1,"y",linewidth=3,label="最小二乘法拟合")

# 增加一列
data['预测点赞数'] = y1

should_better_title_data = data[data['点赞数']>data['预测点赞数']*(1.5)]
title_pie_data = data[data['点赞数']<data['预测点赞数']*(0.5)]

sbtd_x = should_better_title_data['阅读数'].values.tolist()
sbtd_y = should_better_title_data['点赞数'].values.tolist()
plt.scatter(x=sbtd_x,y=sbtd_y,label="标题有待优化的文章(覆盖了部分实际值)",c='green')

tpd_x = title_pie_data['阅读数'].values.tolist()
tpd_y = title_pie_data['点赞数'].values.tolist()
plt.scatter(x=tpd_x,y=tpd_y,label="有标题党风险的文章(覆盖了部分实际值)",c='red')

plt.legend()
plt.show()

should_better_title_data.to_excel("标题有待优化的文章.xlsx",index=False)

title_pie_data.to_excel("有标题党风险的文章.xlsx",index=False)