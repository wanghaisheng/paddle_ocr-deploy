'''
#需要将PaddleHub和PaddlePaddle统一升级到2.0版本
pip install paddlehub==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install paddlepaddle==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
#该Module依赖于第三方库shapely、pyclipper，使用该Module之前，请先安装shapely、pyclipper
pip install shapely pyclipper matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install pyclipper -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple 
# 下载模型
hub install resnet50_vd_dishes==1.0.0
hub install mobilenet_v2_dishes==1.0.0
hub install yolov3_mobilenet_v1_coco2017==1.0.2
# 如果GPU显存不够，修改paddlehub\modules\resnet50_vd_dishes\module.py
'''


import paddlehub as hub
import os
from PIL import ImageFont, ImageDraw, Image
import numpy as np


# 加载移动端预训练模型
expect_classes = ['cup', 'bowl']
yolo = hub.Module(name="yolov3_mobilenet_v1_coco2017")
dishes_class = hub.Module(name="mobilenet_v2_dishes")
# dishes_class = hub.Module(name="resnet50_vd_dishes")
print('模型加载完毕: yolov3_mobilenet_v1_coco2017, mobilenet_v2_dishes')

def detect(np_images):
    results = yolo.object_detection(paths=None,
        images=np_images,
        batch_size=1,
        use_gpu=False,
        output_dir='output',
        score_thresh=0.35,
        visualization=False)
    return results


# 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
def classification(np_images):
    results = dishes_class.classification(
        images=np_images,         # 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
        use_gpu=False,            # 是否使用 GPU；若使用GPU，请先设置CUDA_VISIBLE_DEVICES环境变量
        batch_size=1,              # batch 的大小
        top_k=1)                    # 返回预测结果的前 k 个

    # return json.dumps(results)
    return {'code': 0, 'result': results}

def crop(np_image, detected_data):
    height = int(detected_data['bottom'] - int(detected_data['top']))
    top = int(detected_data['top']) - height
    if top < 0 :
        top = 0
    return np_image[top:int(detected_data['bottom']), int(detected_data['left']):int(detected_data['right'])]

def draw_boxes(draw_img, all_data, box_color = (255,0,255), label_color=(0,0,0)):
    data = all_data['data']

    fontpath = "./font/alifont.ttf"
    font = ImageFont.truetype(fontpath, 16)
    img_pil = Image.fromarray(draw_img)
    draw = ImageDraw.Draw(img_pil)
    #绘制文字信息<br># (100,300/350)为字体的位置，(255,255,255)为白色，(0,0,0)为黑色


    for d in data:
        label = d['label']
        labelSize = draw.textsize(label, font=font, spacing=4, direction=None, features=None, language=None, stroke_width=0)

        if d['top']- labelSize[1] - 3 < 0:
            draw.rectangle(((int (d['left']), int(d['top'] + 2)), (int(d['right'] + labelSize[0]), int(d['bottom'] + labelSize[1] + 3))),fill=None,outline=box_color, width=2)
            draw.text((int(d['left']), int(d['top'] + labelSize[1] + 3)),  label, font = font, fill = label_color)
        else:
            draw.rectangle(((int(d['left']), int(d['top'] - labelSize[1] - 3)), (int(d['right'] + labelSize[0]), int(d['bottom'] - 3))),fill=None,outline=box_color, width=2)
            draw.text( (int(d['left']), int(d['top'] - 3)),  label, font = font, fill = label_color)
    return np.array(img_pil)

def dishesClassify(np_images):
    detect_results = detect(np_images)
    dish_images = []
    dish_data = []
    source_img_index = -1
    result = []
    for np_image, deteced_images in zip(np_images, detect_results):
        # 结果以原始图片分组
        result.append({'data': []})
        source_img_index += 1

        # 检测碗和杯子
        for detected_data in deteced_images['data']:
            if detected_data['label'] in expect_classes:
                detected_data['source_img_index'] = source_img_index
                dish_data.append(detected_data)
                dish_images.append(crop(np_image, detected_data))
                

    # 菜品识别
    class_results = classification(dish_images)

    # 拼装返回值
    if class_results['code'] == 0:
        for results_result, data in zip(class_results['result'], dish_data):
            for label in results_result.keys():
                confidence = results_result[label]
                index = data['source_img_index']
                data['label']= label
                data['confidence']= confidence
            r = result[index]
            r['data'].append(data)
    return result

if __name__ == '__main__':
    # import matplotlib.pyplot as plt 
    # import matplotlib.image as mpimg 
    import cv2

    # 读取测试文件夹test.txt中的照片路径
    np_images =[cv2.imread(image_path) for image_path in ['./data/dishes1.jpeg', './data/dishes2.jpeg']] 
    results = dishesClassify(np_images)
    index = 0
    for image, data in zip(np_images, results):
        im = draw_boxes(image, data)
        cv2.imwrite('./output/np_images_'+ str(index) +'.jpg', im)
        index += 1

    print('results:', results)