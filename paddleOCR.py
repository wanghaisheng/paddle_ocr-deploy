'''
#需要将PaddleHub和PaddlePaddle统一升级到2.0版本
pip install paddlehub==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install paddlepaddle==2.1.1 -i https://pypi.tuna.tsinghua.edu.cn/simple 
#该Module依赖于第三方库shapely、pyclipper，使用该Module之前，请先安装shapely、pyclipper
pip install shapely -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install pyclipper -i https://pypi.tuna.tsinghua.edu.cn/simple 
pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple 
# 下载模型
hub install chinese_ocr_db_crnn_mobile==1.1.2
hub install chinese_ocr_db_crnn_server==1.1.2

'''


import paddlehub as hub
import json


# 待预测图片
test_img_path = []

# 加载移动端预训练模型
ocr = hub.Module(name="chinese_ocr_db_crnn_mobile")
# 服务端可以加载大模型，效果更好 
# ocr = hub.Module(name="chinese_ocr_db_crnn_server") 

# 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
def recognize_text(np_images, thresh):
    results = ocr.recognize_text(
        images=np_images,         # 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
        use_gpu=False,            # 是否使用 GPU；若使用GPU，请先设置CUDA_VISIBLE_DEVICES环境变量
        output_dir='ocr_result',  # 图片的保存路径，默认设为 ocr_result；
        visualization=False,       # 是否将识别结果保存为图片文件；
        box_thresh=0.5,           # 检测文本框置信度的阈值；
        text_thresh=thresh)          # 识别中文文本置信度的阈值；
    # return json.dumps(results)
    return {'code': 0, 'result': results}

if __name__ == '__main__':
    # import matplotlib.pyplot as plt 
    # import matplotlib.image as mpimg 
    import cv2

    with open('test.txt', 'r') as f:
        test_img_path=[]
        for line in f:
            test_img_path.append(line.strip())

            # 展示其中广告信息图片
            # img1 = mpimg.imread(line.strip()) 
            # plt.figure(figsize=(10,10))
            # plt.imshow(img1) 
            # plt.axis('off') 
            # plt.show()

    # 读取测试文件夹test.txt中的照片路径
    np_images =[cv2.imread(image_path) for image_path in test_img_path] 
    results = recognize_text(np_images, 0.6)
    '''
    results = ocr.recognize_text(
                        images=np_images,         # 图片数据，ndarray.shape 为 [H, W, C]，BGR格式；
                        use_gpu=False,            # 是否使用 GPU；若使用GPU，请先设置CUDA_VISIBLE_DEVICES环境变量
                        output_dir='ocr_result',  # 图片的保存路径，默认设为 ocr_result；
                        visualization=True,       # 是否将识别结果保存为图片文件；
                        box_thresh=0.5,           # 检测文本框置信度的阈值；
                        text_thresh=0.5)          # 识别中文文本置信度的阈值；

    for result in results:
        data = result['data']
        save_path = result['save_path']
        for infomation in data:
            print('text: ', infomation['text'], '\nconfidence: ', infomation['confidence'], '\ntext_box_position: ', infomation['text_box_position'])
    '''
    print('results:', results)