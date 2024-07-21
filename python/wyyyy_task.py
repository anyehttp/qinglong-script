import asyncio
import aiohttp
import os
import random
import requests
#先在此网站登录https://wyy.ukzs.net/ 然后添加wyyyy_data(Cookie)和bark_url(bark链接如：https://api.day.app/xxxxxxxxx/)

def get_random_element(arr):
    return random.choice(arr)

def get_random_user_agent():
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
    browser_versions = {
        'Chrome': ['91.0.4472.124', '92.0.4515.107', '93.0.4577.82'],
        'Firefox': ['89.0', '90.0', '91.0'],
        'Safari': ['14.0.3', '14.1.2', '15.0'],
        'Edge': ['91.0.864.67', '92.0.902.55', '93.0.961.38'],
        'Opera': ['77.0.4054.277', '78.0.4093.112', '79.0.4143.72']
    }
    os = ['Windows NT 10.0; Win64; x64', 'Macintosh; Intel Mac OS X 10_15_7', 'X11; Linux x86_64']
    webkit_version = ['537.36', '605.1.15']

    browser = get_random_element(browsers)
    version = get_random_element(browser_versions[browser])
    operating_system = get_random_element(os)
    webkit = get_random_element(webkit_version)

    if browser == 'Safari':
        return f"Mozilla/5.0 ({operating_system}) AppleWebKit/{webkit} (KHTML, like Gecko) Version/{version} Safari/{webkit}"
    return f"Mozilla/5.0 ({operating_system}) AppleWebKit/{webkit} (KHTML, like Gecko) {browser}/{version} Safari/{webkit}"



async def 云贝签到(session, data):
    print('云贝签到启动')
    async with session.post('https://wyy.ukzs.net/api/yunbei/signs', data=data) as response:
        dic = await response.json()
        if dic['code'] == 200:
            print(f'云贝签到成功')
            print(dic)
            return '云贝签到成功'
        else:
            print(f'云贝签到失败可能是ck到期{dic}')
            print(dic)
            return '云贝签到失败'
        

async def 签到(session, data):
    print('签到启动')
    async with session.post('https://wyy.ukzs.net/api/daily_signin', data=data) as response:
        dic = await response.json()
        if dic['code'] == 200:
            print(f'签到成功')
            print(dic)
            return '签到成功'
        else:
            print(f'签到失败可能是ck到期{dic}')
            print(dic)
            return '签到失败'

        

async def 刷歌(session, data):
    print('刷歌启动')
    async with session.post('https://wyy.ukzs.net/api/personalized', data=data) as response:
        dic = await response.json()
        if dic['code'] == 200:
            print(f'刷歌成功')
            print(dic)
            return '刷歌签到成功'
        else:
            print(f'刷歌失败可能是ck到期{dic}')
            return '刷歌签到失败'





async def 原神启动(session, Cookie):
    data = {"limit":10,"cookie":f"{Cookie}"}
    print('刷歌启动中')
    刷歌_data = await 刷歌(session, data)
    print('签到启动中')
    签到_data = await 签到(session, data)
    print('云贝签到启动中')
    云贝签到_data = await 云贝签到(session, data)
    return f'{签到_data} {云贝签到_data} {刷歌_data}'




async def main():
    random_user_agent = get_random_user_agent()
    print(f'随机User-Agent：{random_user_agent}')

    print('获取cookie和bark')
    Cookie = os.getenv('wyyyy_data')
    bark = os.getenv('bark_url')
     

    if not Cookie:
        print('请设置环境变量wyyyy_data')
        return
    if not bark:
        print('请设置环境变量bark_url')
        return

       
    Cookie = Cookie.split('&')
    账号数量 = len(Cookie)
    print(f'检测到有{账号数量}个账号')

    
    headers = {
        'User-Agent':f'{random_user_agent}',
        'Cookie': f'{Cookie}',
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:

        print('！！！！！！！！！！原神启动！！！！！！！！！！！！')
        tasks = [
            原神启动(session, Cookie)
            for Cookie in Cookie]


        resp = await asyncio.gather(*tasks)

        通知 = ''

        for i, ranges in zip(range(1, len(resp) + 1), resp):
            
            通知 += f'账号{i}-{ranges}\n'

        print(通知)

        print('！！！！！！！！！！原神启动完成！！！！！！！！！！！！')

        print('发送通知')
        requests.get(f'{bark}{通知}')


if __name__ == '__main__':
    asyncio.run(main())
