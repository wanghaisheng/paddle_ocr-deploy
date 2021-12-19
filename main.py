'''
pip install fastapi pydantic uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple 

'''
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
import uvicorn
import cv2
import numpy as np

import paddleOCR as ocr
import sentimentAnalysis as sa

app = FastAPI() # 创建 api 对象
templates = Jinja2Templates(directory="./template")
app.mount("/_assets", StaticFiles(directory="./template/_assets"), name="_assets")

class R_Text(BaseModel):
    text: list = []


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
        imgs.append(cv2.imdecode(nparr, cv2.IMREAD_COLOR))

    return ocr.recognize_text(imgs , 0.6)

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