# _*_ coding: utf-8 _*_

'''
#需要将PaddleHub和PaddlePaddle统一升级到2.0版本
pip install paddlehub==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install paddlepaddle==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
# 下载模型
hub install deoldify==1.0.1
# 如果GPU显存不够，修改paddlehub\modules\resnet50_vd_dishes\module.py
'''


import paddlehub as hub
import os
import tempfile
import cv2

deoldify = hub.Module(name="deoldify")
print('模型加载完毕: deoldify')

# 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
def colorization(np_array):
    base_path = './output/deoldify_data'
    if os.path.exists( base_path) == False:
        os.makedirs( base_path )
    fd, file_path = tempfile.mkstemp(suffix='.jpg', prefix='source_', dir=base_path, text=False)
    cv2.imwrite(file_path, np_array)
    return colorization_file(file_path)

def colorization_file(path):
    results = deoldify.predict(path)
    # return json.dumps(results)
    return {'code': 0, 'result': results}

if __name__ == '__main__':
    content =cv2.imread('./data/black.JPG')
    results = colorization(content)
    print(results)