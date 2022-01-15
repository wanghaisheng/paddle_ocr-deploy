# _*_ coding: utf-8 _*_

'''
#需要将PaddleHub和PaddlePaddle统一升级到2.0版本
pip install paddlehub==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install paddlepaddle==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
# 下载模型
hub run stylepro_artistic
# 如果GPU显存不够，修改paddlehub\modules\resnet50_vd_dishes\module.py
'''


import paddlehub as hub
import os
import numpy as np


artistic = hub.Module(name="stylepro_artistic")
print('模型加载完毕: stylepro_artistic')

# 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
def style_transfer(content, styles, alpha=1):
    images=[{
        'content': content,
        'styles': styles
    }]
    results = artistic.style_transfer(
        images=images,         # 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
        use_gpu=False,            # 是否使用 GPU；若使用GPU，请先设置CUDA_VISIBLE_DEVICES环境变量
        output_dir='output',  # 图片的保存路径，默认设为 ocr_result；
        visualization=False,       # 是否将识别结果保存为图片文件；
        alpha=alpha)          # 转换的强度，[0, 1] 之间，默认值为1；

    # return json.dumps(results)
    return {'code': 0, 'result': results}

if __name__ == '__main__':
    # import matplotlib.pyplot as plt 
    # import matplotlib.image as mpimg 
    import cv2

    content =cv2.imread('./data/pic_part_4.jpg')
    styles =[cv2.imread(image_path) for image_path in ['./data/artists/fangao.jpeg', './data/artists/monai.jpeg', './data/artists/qibaishi.jpeg','./data/artists/xinhaicheng.jpeg']] 
    index = 0
    for style in styles:
        results = style_transfer(content, [style], 1)
        result = results['result'][0]['data']
        cv2.imwrite('./output/pic_'+ str(index) +'.jpg', result)
        index += 1