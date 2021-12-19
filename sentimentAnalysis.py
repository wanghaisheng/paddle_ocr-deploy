'''
#需要将PaddleHub和PaddlePaddle统一升级到2.0版本
pip install paddlehub==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install paddlepaddle==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install paddlenlp -i https://pypi.tuna.tsinghua.edu.cn/simple 

'''


from paddlenlp import Taskflow

senta = Taskflow("sentiment_analysis")

# 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
def analysis(text):
    results = senta(text)
    # return json.dumps(results)
    return {'code': 0, 'result': results}

if __name__ == '__main__':
    txt = ['光明网12月18日讯今天下午，国务院联防联控机制召开新闻发布会，介绍科学精准做好元旦春节期间疫情防控有关情况。',
        '国家卫生健康委疾控局一级巡视员贺青华表示，2022年元旦春节即将到来，北京冬奥会、冬残奥会等重大活动即将举办。目前，全球疫情防控形势依然严峻复杂，很多国家疫情仍在高位流行，奥密克戎变异株已在全球70多个国家和地区传播。',
        '他强调，今年“两节”期间疫情防控必须高度重视，不能有丝毫的麻痹大意。各项措施要在总结2021年“两节”期间疫情防控经验的基础上，更加突出科学精准，强化人员安全有序流动，确保群众度过健康平安的节日。',
        '贺青华介绍，一是个人外出和返乡时要做好个人防护，包括戴口罩、勤洗手，不扎堆，不聚集，1米线，保持良好的卫生习惯和健康的生活方式，积极接种新冠病毒疫苗，做到应接尽接。']
    print('results:', analysis(txt))