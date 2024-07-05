import requests
import os
from bs4 import BeautifulSoup

#频道:https://t.me/IPAs_share
#群组:https://t.me/IPAs_Dd

#一个监控AppStore软件本体和内购价格的脚本，青龙创建requests，os，bs4依赖

#环境变量设置：
#设置环境变量app_data 值为 要监控的app，AppStore链接里面的 地区 名字 和id：{"地区":["us", "us", "us"], "名字":["code-app", "青龙面板", "surge-5"], "id":[1512938504, 6466607641, 1442620678], "购买方式":["本体", "内购", "内购"]}
#bark通知-设置环境变量名为 app_bark 值为：https://api.day.app/xxxxxx/
def bark(notice):
    bark_url = os.getenv('app_bark')
    requests.get(f'{bark_url}{notice}')


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
}

def request_url(url):
    with requests.Session() as session:
        url_html = session.get(url, headers=headers)
        url_html.encoding = 'utf-8'
        return url_html

#app本体
def BeautifulSoup_本体_html(price):
    soup = BeautifulSoup(price.text, 'html.parser')
    price_element = soup.find('li', class_='inline-list__item inline-list__item--bulleted app-header__list__item--price')
    return price_element

#app内购
def BeautifulSoup_内购_html(price):
    soup = BeautifulSoup(price.text, 'html.parser')
    app_titles = soup.find_all('span', class_='truncate-single-line truncate-single-line--block')
    app_prices = soup.find_all('span', class_='list-with-numbers__item__price small-hide medium-show-tablecell')
    return app_titles, app_prices



def main():
    # 读取环境变量中的app数据
    app_数据 = os.getenv('app_data')
    #app_数据 = os.getenv('app_data', '{"地区":["us", "us", "us"], "名字":["code-app", "青龙面板", "surge-5"], "id":[1512938504, 6466607641, 1442620678], "购买方式":["本体", "内购", "内购"]}')
    
    # 使用eval解析字符串成字典
    app_数据 = eval(app_数据)  

    #对比数据
    assert len(app_数据['地区']) == len(app_数据['名字']) == len(app_数据['id']) == len(app_数据['购买方式'])
    
    #备用空字符
    notice = ''
    
    #打包成zip遍历
    for 地区, 名字, id, 购买方式 in zip(app_数据['地区'], app_数据['名字'], app_数据['id'], app_数据['购买方式']):
        url = f'https://apps.apple.com/{地区}/app/{名字}/id{id}'
        url_html = request_url(url)
        
        
        #判断是否为本体
        if 购买方式 == '本体':
            BeautifulSoup_price = BeautifulSoup_本体_html(url_html)
            if BeautifulSoup_price:
                print(名字, 购买方式, BeautifulSoup_price.text.strip())
                notice_bark = f"{名字}-{购买方式}-{BeautifulSoup_price.text.strip()}"
                notice += notice_bark + '\n' + '-----------' + '\n'
        else :
            app_titles, app_prices = BeautifulSoup_内购_html(url_html)
            if app_titles and app_prices:
                for title, price in zip(app_titles, app_prices):
                    print(名字, 购买方式, title.text.strip(), price.text.strip())
                    notice_bark = f"{名字}-{购买方式}-{title.text.strip()}-{price.text.strip()}"
                    notice += notice_bark + '\n' + '-----------' + '\n'
            
    #调用通知函数
    bark(notice)

if __name__ == '__main__':
    main()
