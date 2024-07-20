import os
import time
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

# 通知函数，使用 Bark 服务发送通知
async def bark(notice):
    async with aiohttp.ClientSession() as session:
        notice_encoded = urllib.parse.quote(notice)
        bark_url = os.getenv('app_bark')
        if bark_url:
            await session.get(f'{bark_url}{notice_encoded}')
        else:
            print("Bark URL 未设置，请检查环境变量 app_bark")

# 模拟浏览器请求的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
}

# 异步get请求，获取URL的HTML内容
async def request_url(url, session):
    async with session.get(url, headers=headers) as response:
        response_text = await response.text()
        return response_text

# 解析app本体价格
def BeautifulSoup_本体_html(price):
    soup = BeautifulSoup(price, 'html.parser')
    price_element = soup.find('li', class_='inline-list__item inline-list__item--bulleted app-header__list__item--price')
    return price_element

# 解析app内购项目
def BeautifulSoup_内购_html(price):
    soup = BeautifulSoup(price, 'html.parser')
    app_titles = soup.find_all('span', class_='truncate-single-line truncate-single-line--block')
    app_prices = soup.find_all('span', class_='list-with-numbers__item__price small-hide medium-show-tablecell')
    return app_titles, app_prices

# 读取本地 app_data.json 文件
def read_local_data(filename='app_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 写入本地 app_data.json 文件
def write_local_data(data, filename='app_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 获取app数据并解析价格
async def fetch_app_data(地区, 名字, id, 购买方式, session):
    url = f'https://apps.apple.com/{地区}/app/{名字}/id{id}'
    url_html = await request_url(url, session)
    
    if 购买方式 == '本体':
        BeautifulSoup_price = BeautifulSoup_本体_html(url_html)
        if BeautifulSoup_price:
            return {'name': 名字, 'type': 购买方式, 'id': id, 'price': BeautifulSoup_price.text.strip()}
    else:
        app_titles, app_prices = BeautifulSoup_内购_html(url_html)
        if app_titles and app_prices:
            return [{'name': 名字, 'type': 购买方式, 'id': id, 'price': price.text.strip(), 'title': title.text.strip()} for title, price in zip(app_titles, app_prices)]
    return None

# 主函数
async def main():
    # 读取环境变量中的app数据
    app_数据 = os.getenv('app_data')
    if not app_数据:
        print("环境变量 app_data 未设置，请检查")
        return

    app_数据 = json.loads(app_数据)  # 使用 json.loads() 来解析 JSON 字符串
    
    # 检查数据完整性
    assert len(app_数据['地区']) == len(app_数据['名字']) == len(app_数据['id']) == len(app_数据['购买方式'])
    
    local_data = read_local_data()

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_app_data(地区, 名字, id, 购买方式, session)
            for 地区, 名字, id, 购买方式 in zip(app_数据['地区'], app_数据['名字'], app_数据['id'], app_数据['购买方式'])
        ]
        
        results = await asyncio.gather(*tasks)
        notice = []

        for result in results:
            if result:
                if isinstance(result, list):
                    for index, item in enumerate(result):
                        key = f"{item['name']}-{item['title']}-{index}"  # 添加唯一索引值
                        if key in local_data:
                            if local_data[key]['price'] != item['price']:
                                notice.append(f"{item['name']} {item['title']} {local_data[key]['price']} -> {item['price']}")
                        else:
                            notice.append(f"添加 {item['name']} {item['title']} {item['price']}")
                        local_data[key] = item
                else:
                    key = f"{result['name']}-{result['id']}"
                    if key in local_data:
                        if local_data[key]['price'] != result['price']:
                            notice.append(f"{result['name']} {local_data[key]['price']} -> {result['price']}")
                    else:
                        notice.append(f"添加 {result['name']} {result['price']}")
                    local_data[key] = result

        if notice:
            await bark('\n'.join(notice))
        
        write_local_data(local_data)

if __name__ == '__main__':
    t1 = time.time()
    asyncio.run(main())
    t2 = time.time()
    print('共耗时:', t2 - t1, '秒')
