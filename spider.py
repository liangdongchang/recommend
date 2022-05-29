import json
import time
import urllib.request, urllib.error  # 制定url，获取网页数据
import xlwt  # 进行excel操作
from bs4 import BeautifulSoup  # 网页解析，获取数据

# URL的网页内容
def ask_url(url):  # 模拟浏览器头部信息，向服务器发送消息
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34"
    }  # 用户代理：表示告诉目标服务器，我们是什么类型的机器；浏览器：本质上告诉服务器，我们能够接收什么水平的内容
    request = urllib.request.Request(url, headers=head)
    html = ""  # 存储
    try:
        response = urllib.request.urlopen(request)  # 传递封装好的request对象，包含所访问的网址和头部信息
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)  # 打印出code的变量
        if hasattr(e, "reason"):  # 打印出什么原因导致未捕获成功
            print(e.reason)
    return html


def save_img(url, name):
    # 保存图片
    filename = 'media/health_cover/{}.jpg'.format(name)
    # head = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34"
    # }  # 用户代理：表示告诉目标服务器，我们是什么类型的机器；浏览器：本质上告诉服务器，我们能够接收什么水平的内容
    # # request = urllib.request.Request(url, headers=head)
    # # response = urllib.request.urlopen(request)
    # r = requests.get(url,headers=head)
    # with open('movie_cover/{}.jpg'.format(name), 'wb') as f:
    #     f.write(r.content)

    # urllib.request.urlretrieve(url, filename=filename)
    # 方式1
    try:
        head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }
        request = urllib.request.Request(url, headers=head)
        response = urllib.request.urlopen(request, timeout=10)

        with open(filename, 'wb') as f:
            f.write(response.read())
        return True
    except:
        pass
    return False


def save_txt(data):
    # 保存为txt文件
    with open('春雨医生健康知识.txt', 'a') as f:
        f.write(json.dumps(data))
        f.write('\r\n')


def read_txt():
    # 读取txt文件
    data_list = []
    with open('春雨医生健康知识.txt', 'r') as f:
        for data in f.readlines():
            if data != '\n' and data not in data_list:
                data_list.append(json.loads(data))
    return data_list


def get_data(url):
    # 获取数据
    print('url',url)
    html = ask_url(url)
    soup = BeautifulSoup(html, "html.parser")
    d_dict = {}
    div = soup.find('div', class_='main-wrap')
    if not div:
        return {}
    d_dict['标题'] = div.find('h1').text
    d_dict['时间'] = div.find('p', class_='time').text
    desc = div.find('p', class_='desc')
    d_dict['描述'] = desc.text if desc else '<p></p>'
    content = div.find('div', class_='news-content')
    text = ''
    sections = content.find_all('section')
    if sections:
        for span in content.find_all('span'):
            if '图源：' in span.text:
                continue
            text += '<p>'
            text += span.text
            text += '</p>'
        # for section in sections:
        #     span = section.find('span')
        #     if not span:
        #         span = section.find('strong')
        #     if not span:
        #         continue
        #
        #     if '图源：' in span.text:
        #         continue
        #     text += '<p>'
        #     text += span.text
        #     text += '</p>'
    else:
        ps = content.find_all('p')
        for p in ps:
            spans = p.find_all('span')
            if not spans:
                text += '<p>'
                text += p.text
                text += '</p>'
                continue
            text += '<p>'
            for span in spans:
                if '图源：' in span.text:
                    text += '</p>'
                    continue
                text += '<span>'
                text += span.text
                text += '</span>'
            text += '</p>'

    d_dict['内容'] = text.replace('\xa0', '')
    print(d_dict['内容'])
    time.sleep(1)
    return d_dict


def save_xls(datalist, savepath):
    # 保存数据到表格
    print("save...")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('豆瓣电影TOP250', cell_overwrite_ok=True)  # 创建工作表，第二个参数是覆盖以前的数据
    col = ('电影名', '详情链接', '观看链接', '导演', '编剧', '主演', '类型', '制片国家/地区', '语言',
           '上映日期', '片长', '又名', 'IMDb', '封面链接', '评分',
           '简介')  # 元组

    for i in range(0, len(col)):
        sheet.write(0, i, col[i])  # 列名

    for i in range(0, len(datalist)):
        print("第%d条" % i, datalist[i])
        data = datalist[i]
        for j in range(0, len(col)):
            if col[j] in data:
                d = data[col[j]]
            else:
                d = ''
            sheet.write(i + 1, j, d)  # 数据
    book.save(savepath)  # 保存数据表


def get_page_urls(url):
    # 获取每一页的文章的url
    html = ask_url(url)
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    ul = soup.find('ul', class_='health-news-list').find_all('li')
    for li in ul:
        url = 'https://www.chunyuyisheng.com/{}'.format(li.find('a', class_='info-pic-wrap').attrs['href'])
        img = li.find('img').attrs['src']
        code = url.split('article')[1].replace('/', '')
        save_img(img, code)
        urls.append([url, code])
    time.sleep(1)
    return urls

def get_all_urls(url):
    # 获取所有要爬取的页面url
    html = ask_url(url)
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find('ul', id='channel').find_all('li')
    urls = {}
    for li in ul:
        urls[li.text.replace('\n', '').replace('\t', '')] = 'https://www.chunyuyisheng.com/{}'.format(li.a.attrs['href'])
    time.sleep(1)
    return urls

def get_all_data(baseurl):
    # 获取页面电影url
    d_list = []

    urls = get_all_urls(baseurl)  # 获取各类别的url
    for name,url in urls.items():
        print('爬取 {} 的数据'.format(name))
        page_urls = get_page_urls(url) # 获取类别下的文章url
        for pu in page_urls:
            d_dict = get_data(pu[0])
            if not d_dict:
                continue
            d_dict['code'] = pu[1]
            d_dict['类别'] = name
            save_txt(d_dict)
            print(d_dict)
            d_list.append(d_dict)
            time.sleep(1)

    return d_list


def main(baseurl):
    '''
    :param baseurl:
    :return:
    '''
    datalist = get_all_data(baseurl)
    # savepath = "春雨医生健康知识.xls"  # 当前目录新建Excel，存储数据
    # save_xls(datalist, savepath)  # 存于Excel表



if __name__ == '__main__':
    baseurl = 'https://www.chunyuyisheng.com/pc/health_news/'
    main(baseurl)
