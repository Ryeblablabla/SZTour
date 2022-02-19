#coding=utf-8
import urllib.request
import urllib.parse
import re
from tqdm import tqdm
import pandas as pd
from lxml import etree
from jieba import analyse
# 引入TF-IDF关键词抽取接口
tfidf = analyse.extract_tags
import py2neo
from py2neo import Graph,Node,Relationship,NodeMatcher
import csv

resultText1 = "crawlerResult.txt"
resultText2 = "HandleResult.txt"
resultText3 = "data/relation.csv"
# 保存文件的文件名
relationNames = {'地理位置', '邮政区码', '门票价格', '馆长', '馆藏精品',\
                 '竣工时间', '所属城市', '气候条件', '电话区号', '预定电话',\
                 '外文名', '景点级别', '面积', '建议游玩时长', '占地面积',\
                 '海拔高度', '人口数量', '被联合国列为', '吴中区', '编号',\
                 '所属地区', '类别', '火车站', '地点', '保护级别', '所处时代',\
                 '行政区类别', '著名景点', '别名', '所属宗派', '车牌代码', '始建',\
                 '地区生产总值', '官方电话', '海拔', '下辖地区', '管理单位',\
                 '所属国家', '开放时间', '批准单位', '适宜游玩季节'}
# 预处理存储标签信息
attriDict = {}
typelists = {'attractions','level','location','price','climate','time','others'}

def detect(s):
    if attriDict.get(s) == None:
        if "级" in s or "重点" in s:
            return "level"
        for item in ("省","市","国","县","镇"):
            if item in s:
                return "location"
        if "元" in s:
            return "price"
        if "气候" in s or "季" in s:
            return "climate"
        if "年" in s or "月" in s or "日" in s or "周" in s:
            return "time"
        return "others"
    return attriDict.get(s)

def query(url):
    # 请求头部
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 利用请求地址和请求头部构造请求对象
    req = urllib.request.Request(url=url, headers=headers, method='GET')
    # 发送请求，获得响应
    response = urllib.request.urlopen(req)
    # 读取响应，获得文本
    text = response.read().decode('utf-8')
    # 构造 _Element 对象
    html = etree.HTML(text)
    # 使用 xpath 匹配数据，得到匹配字符串列表
    # print(text)

    # 爬取简介信息
    sen_list = html.xpath('//div[contains(@class,"lemma-summary") or contains(@class,"lemmaWgt-lemmaSummary")]//text()')
    # 过滤数据，去掉空白
    sen_list_after_filter = [item.strip('\n') for item in sen_list]

    value_list = html.xpath('//div[contains(@class,"basic-info J-basic-info cmn-clearfix")]//text()')
    # 爬取标签
    # print(value_list)
    value_list_after_filter = [item.strip('\n') for item in value_list]
    # 过滤数据，去掉空白

    newvaluelst = []
    for item in value_list_after_filter:
        newstr = "".join(item.split())
        newvaluelst.append(newstr)
    # print(newvaluelst)

    # 将字符串列表连成字符串并返回
    return ''.join(sen_list_after_filter) + '\n' + ' '.join(newvaluelst) + '\n'

# 初始化URL列表
URLlist = []

def add(url, name):
    URLlist.append((url, name))
    attriDict[name] = "attractions"

add("https://baike.baidu.com/item/%E6%8B%99%E6%94%BF%E5%9B%AD/154079", "拙政园")
add("https://baike.baidu.com/item/%E7%95%99%E5%9B%AD/453654", "留园")
add("https://baike.baidu.com/item/%E7%BD%91%E5%B8%88%E5%9B%AD", "网师园")
add("https://baike.baidu.com/item/%E8%99%8E%E4%B8%98%E5%B1%B1%E9%A3%8E%E6%99%AF%E5%90%8D%E8%83%9C%E5%8C%BA/5635377",
    "虎丘")
add("https://baike.baidu.com/item/%E5%91%A8%E5%BA%84%E9%95%87/6131", "周庄")
add("https://baike.baidu.com/item/%E5%AF%92%E5%B1%B1%E5%AF%BA/414574", "寒山寺")
add("https://baike.baidu.com/item/%E7%8B%AE%E5%AD%90%E6%9E%97/1025067", "狮子林")
add("https://baike.baidu.com/item/%E5%A4%A9%E5%B9%B3%E5%B1%B1%E9%A3%8E%E6%99%AF%E5%90%8D%E8%83%9C%E5%8C%BA", "天平山")
add("https://baike.baidu.com/item/%E7%A9%B9%E7%AA%BF%E5%B1%B1", "穹窿山")
add("https://baike.baidu.com/item/%E6%B2%A7%E6%B5%AA%E4%BA%AD/215979", "沧浪亭")
add("https://baike.baidu.com/item/%E8%8B%8F%E5%B7%9E%E5%8D%9A%E7%89%A9%E9%A6%86/1629584", "苏州博物馆")
add("https://baike.baidu.com/item/%E9%87%91%E9%B8%A1%E6%B9%96/2376478", "金鸡湖")
add("https://baike.baidu.com/item/%E6%9C%A8%E6%B8%8E%E5%8F%A4%E9%95%87", "木渎古镇")

with open(resultText1, 'w', encoding="utf-8") as f:
    print("正在爬取网络数据：")
    for item, name in tqdm(URLlist):
        result = query(item)
        # print(result)
        f.write(name + '\n')
        f.write(result + '\n')
# 存储爬虫结果文本

print("正在处理文本结果")
# 利用正则表达式处理文本
with open(resultText1, 'r', encoding="utf-8") as f:
    TextList = f.read()
    pattern = re.sub(u"\\[.*?]", "", TextList)
    # 去除掉所有从百度百科爬取的中括号
    pattern2 = re.sub(u"、", " ", pattern)
    # 去除掉所有顿号
    with open(resultText2, 'w', encoding="utf-8") as f2:
        f2.write(pattern2)

resultDict = {'entity1':[],'entity2':[],'relation':[]}

with open(resultText2, 'r', encoding="utf-8") as f:
    lines = f.readlines()
    for i in range(0,4*len(URLlist)-3,4):
        tourName = lines[i].strip('\n')
        summaryText = lines[i+1]
        labelLists = lines[i+2].split()
        relationName = labelLists[2]
        idx = 0
        for item in labelLists:
            idx+=1
            if idx <= 2:
                continue
            if item in relationNames:
                relationName = item
                continue
            if item == "国家AAAAA级旅游景区":
                item = "AAAAA级"
            elif item == "国家级AAAA景区":
                item = "AAAA级"
            resultDict['entity1'].append(tourName)
            resultDict['relation'].append(relationName)
            resultDict['entity2'].append(item)

df = pd.DataFrame(resultDict)

# index=False表示不写入索引
df.to_csv(resultText3, index=False, encoding="utf_8_sig")

print("正在绘制知识图谱")
g=Graph('http://localhost:7474',user='neo4j',password='neo4j')
g.run('match (n) detach delete n')
with open('relation.csv','r',encoding='utf-8') as f:
    reader = csv.reader(f)
    for item in reader:
        if reader.line_num == 1:
            continue
        type1 = detect(item[0])
        type2 = detect(item[1])
        node1 = Node(type1,name=item[0])
        node2 = Node(type2,name=item[1])
        relation = Relationship(node1,item[2],node2)
        g.merge(node1,type1,"name")
        g.merge(node2,type2,"name")
        g.merge(relation,"Relation","name")
