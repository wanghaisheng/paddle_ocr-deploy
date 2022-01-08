import requests
import time
import json

baidu_url='https://aip.baidubce.com'

oauth_url='{baidu_url}/oauth/2.0/token?grant_type=client_credentials&client_id={appid}&client_secret={appkey}'
texttrans_url='{baidu_url}/rpc/2.0/mt/texttrans/v1?access_token={access_token}'
expire_time=0
access_token=''
session_key=''
session_secret=''

def getAccessToken(appid, appkey):
    global expire_time
    global access_token
    global session_key
    global session_secret

    now = int(time.time())
    if access_token == '' or now > expire_time:
        host = oauth_url.format(baidu_url=baidu_url,appid=appid,appkey=appkey)
        response = requests.get(host)
        if response:
            if (not hasattr(response, 'error')):
                text = json.loads(response.text)
                access_token = text['access_token']
                session_key = text['session_key']
                session_secret = text['session_secret']
                expire_time = now + text['expires_in']
    
    return access_token

def texttrans(s, appid, appkey, lang_from='auto', lang_to='en'):
    a_token = getAccessToken(appid, appkey)
    url = texttrans_url.format(baidu_url=baidu_url, access_token=a_token)
    body = {"from": lang_from, "to": lang_to, "q": s}
    response = requests.post(url, data = json.dumps(body))
    return response

if __name__ == '__main__':

    appid='Z2S7BV5GNhwBpBPGtjGrpyxf'
    appkey='uVpGB27MtCGnAF2AxcZYTFYks1SS1Pss'
    lang_from='zh'
    lang_to='en'

    response = texttrans('3.代收银公式，按笔收费 都为按照相应配置生成结算单，如图3.14.4-5代收银配置扫码及结算单生成返还扫码金额，图3.14.4-6按笔收费现金1元，则当期按笔收费结算单=当期结算单所有销售单为现金的必输*1。', appid, appkey)
    print(response.json())
