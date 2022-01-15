'''
pip install fastapi pydantic uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple 

'''
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

from PIL import Image
from io import BytesIO
import os
from pydantic import BaseModel
import aiofiles
import uvicorn
import cv2
import numpy as np

import sentimentAnalysis as sa
import paddleOCR as ocr
# import photo2Cartoon as p2c
import paddleDishes as paddleDishes
import photo2Artist as p2a
import paddleRealSR as realSr
# import paddleColor as colorlization

import image_merge as ImageMerge
import docx_translate as docxTranslate

app = FastAPI() # 创建 api 对象
templates = Jinja2Templates(directory="./template")
app.mount("/_assets", StaticFiles(directory="./template/_assets"), name="_assets")

class R_Text(BaseModel):
    text: list = []

def resize_image(image):
    height, width = image.shape[0], image.shape[1]
    width_new = 1280
    height_new = 720
    scale = 1
    if width / height >= width_new / height_new:
        img_new = cv2.resize(image, (width_new, int(height * width_new / width)), interpolation=cv2.INTER_AREA)
        scale = width_new / width
    else:
        img_new = cv2.resize(image, (int(width * height_new / height), height_new), interpolation=cv2.INTER_AREA)
        scale = height_new / height

    return scale, img_new

def tempFile(module_name, filename):
    base_path = './output/' + module_name
    if os.path.exists( base_path) == False:
        os.makedirs( base_path )
    return base_path + '/' + filename

@app.get("/") # 根路由
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )
@app.post("/cv/ocr/text")
async def recognize_text(images: List[UploadFile] = File(...)):
    imgs = []

    for image in images:
        content = await image.read()
        nparr = np.fromstring(content, np.uint8)
        resize_scale, image_resize = resize_image(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
        imgs.append(image_resize)

    return ocr.recognize_text(imgs , 0.6)

@app.post("/cv/image/merge")
async def merge_images(images: List[UploadFile] = File(...), direct: str=Form(...)):
    imgs = []

    for image in images:
        content = await image.read()
        nparr = np.fromstring(content, np.uint8)
        imgs.append(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

    merged = ImageMerge.mergeImages(imgs, output_color='bgr', direct=direct)
    res, im_jpg = cv2.imencode(".jpg", merged)
    return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")

@app.post("/cv/reg/dishes")
async def recognize_dishes(images: List[UploadFile] = File(...)):
    imgs = None

    for image in images:
        content = await image.read()
        nparr = np.fromstring(content, np.uint8)
        resize_scale, image_resize = resize_image(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
        results = paddleDishes.dishesClassify([image_resize])
        for image, data in zip([image_resize], results):
            imgs = image
            break
    im = paddleDishes.draw_boxes(imgs, data)
    res, im_jpg = cv2.imencode(".jpg", im)
    return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")

# @app.post("/cv/girl/cartoon")
# async def photo2Cartoon(images: List[UploadFile] = File(...)):
#     imgs = None

#     for image in images:
#         content = await image.read()
#         nparr = np.fromstring(content, np.uint8)
#         resize_scale, image_resize = resize_image(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
#         face, imgs = p2c.photo2Cartoon(image_resize)
#         break

#     res, im_jpg = cv2.imencode(".jpg", imgs)
#     return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")

@app.post("/cv/image/artist")
async def photo2Artist(images: List[UploadFile] = File(...), style: int=Form(...)):
    imgs = None
    styleSource =[
        './data/artists/fangao.jpeg', 
        './data/artists/monai.jpeg',
        './data/artists/qibaishi.jpeg',
        './data/artists/xinhaicheng.jpeg']
    if style == None or style < 0 or style > 3:
        style = 0
    styleImg = cv2.imread(styleSource[style])

    for image in images:
        content = await image.read()
        nparr = np.fromstring(content, np.uint8)
        resize_scale, image_resize = resize_image(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
        results = p2a.style_transfer(image_resize, [styleImg], 1)
        imgs = results['result'][0]['data']
        break

    res, im_jpg = cv2.imencode(".jpg", imgs)
    return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")

@app.post("/cv/image/superresolution")
async def superResolution(images: List[UploadFile] = File(...)):
    imgs = None

    for image in images:
        out_file_path = tempFile('real_sr_data', image.filename)
        async with aiofiles.open(out_file_path, 'wb') as out_file:
            content = await image.read()  # async read
            await out_file.write(content)  # async write
            results = realSr.super_resolution_file(out_file_path)
            imgs = results['result']
            res, im_jpg = cv2.imencode(".jpg", imgs)
            return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")


# @app.post("/cv/image/color")
# async def image_color(images: List[UploadFile] = File(...)):
#     imgs = None

#     for image in images:
#         out_file_path = tempFile('deoldify_data', image.filename)
#         async with aiofiles.open(out_file_path, 'wb') as out_file:
#             content = await image.read()  # async read
#             await out_file.write(content)  # async write
#             results = colorlization.colorization_file(out_file_path)
#             imgs = results['result']
#             res, im_jpg = cv2.imencode(".jpg", imgs)
#             return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")


@app.post("/nlp/sentiment/analysis")
async def analysis(text: R_Text):
    if len(text.text) > 0:
        return sa.analysis(text.text)
        # return {'code': -100, 'result': 'Not supported'}
    else:
        return {'code': -999, 'result': 'invalid request'}

@app.post("/nlp/translate/statement")
async def analysis(text: R_Text):
    if len(text.text) > 0:
        statement = ''
        for t in text.text:
            statement = statement.join(t)
        return docxTranslate.translateStatement(statement)
    else:
        return {'code': -999, 'result': 'invalid request'}

if __name__ == "__main__":
    # 启动服务，因为我们这个文件叫做 main.py，所以需要启动 main.py 里面的 app
    # 第一个参数 "main:app" 就表示这个含义，然后是 host 和 port 表示监听的 ip 和端口
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)