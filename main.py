'''
pip install fastapi pydantic uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple 

'''
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

from PIL import Image
from io import BytesIO
from pydantic import BaseModel
import uvicorn
import cv2
import numpy as np

import paddleOCR as ocr
import sentimentAnalysis as sa
import image_merge as ImageMerge

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
async def merge_images(images: List[UploadFile] = File(...), direct: str='horizontal'):
    imgs = []

    for image in images:
        content = await image.read()
        nparr = np.fromstring(content, np.uint8)
        imgs.append(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

    merged = ImageMerge.mergeImages(imgs, output_color='bgr', direct=direct)
    res, im_jpg = cv2.imencode(".jpg", merged)
    return StreamingResponse(BytesIO(im_jpg.tobytes()), media_type="image/jpeg")

@app.post("/nlp/sentiment/analysis")
async def analysis(text: R_Text):
    if len(text.text) > 0:
        return sa.analysis(text.text)
    else:
        return {'code': -999, 'result': 'invalid request'}

if __name__ == "__main__":
    # 启动服务，因为我们这个文件叫做 main.py，所以需要启动 main.py 里面的 app
    # 第一个参数 "main:app" 就表示这个含义，然后是 host 和 port 表示监听的 ip 和端口
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)