import requests
import os
from bs4 import BeautifulSoup

#一个监控AppStore软件本体价格的脚本，青龙创建requests，os，bs4依赖，

#在下面放入bark推送url比如：https://api.day.app/xxxxxxxxx/{notice}
def bark(notice):
    requests.get(f'这里放入bark推送url{notice}')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
}

def request_url(url):
    with requests.Session() as session:
        url_html = session.get(url, headers=headers)
        url_html.encoding = 'utf-8'
        return url_html

def BeautifulSoup_html(price):
    soup = BeautifulSoup(price.text, 'html.parser')
    price = soup.find('li', class_='inline-list__item inline-list__item--bulleted app-header__list__item--price')
    return price



def main():
    # 读取环境变量中的app数据
    app_数据 = os.getenv('app_data')
    #app_data = os.getenv('app_data', '{"地区":["cn", "us"], "名字":["pix站助手-精美二次元壁纸采集工具", "code-app"], "id":[1161125462, 1512938504]}')
    
    app_数据 = eval(app_数据)  # 使用eval解析字符串成字典

    assert len(app_数据['地区']) == len(app_数据['名字']) == len(app_数据['id'])
    
    notice = ''

    for 地区, 名字, id in zip(app_数据['地区'], app_数据['名字'], app_数据['id']):

        url = f'https://apps.apple.com/{地区}/app/{名字}/id{id}'

        url_html = request_url(url)

        BeautifulSoup_price = BeautifulSoup_html(url_html)

        for i in BeautifulSoup_price:
            print(名字, i.text.strip())
            notice_bark = f"{名字} {i.text.strip()}"
            notice += notice_bark + '\n' + '-----------' + '\n'
            
    #调用通知函数
    bark(notice)

if __name__ == '__main__':
    main()
