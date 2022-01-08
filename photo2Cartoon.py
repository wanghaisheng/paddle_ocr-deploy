# _*_ coding: utf-8 _*_

import sys 
import os
import cv2
from PIL import Image
import numpy as np

import paddle
from paddle.utils.download import get_path_from_url
from ppgan.faceutils.dlibutils import align_crop
from ppgan.faceutils.face_segmentation import FaceSeg
from ppgan.models.generators import ResnetUGATITP2CGenerator
from ppgan.apps.base_predictor import BasePredictor


P2C_WEIGHT_URL = "https://paddlegan.bj.bcebos.com/models/photo2cartoon_genA2B_weight.pdparams"

def nparray2Image(img):
    # You may need to convert the color.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img)
    return im_pil

def image2Nparray(im_pil):
    # For reversing the operation:
    im_np = np.asarray(im_pil)
    return im_np


class Photo2CartoonPredictor(BasePredictor):
    def __init__(self, weight_path=None):
        if weight_path is None:
            cur_path = os.path.abspath(os.path.dirname(__file__))
            weight_path = get_path_from_url(P2C_WEIGHT_URL, cur_path)

        self.genA2B = ResnetUGATITP2CGenerator()
        params = paddle.load(weight_path)
        self.genA2B.set_state_dict(params)
        self.genA2B.eval()
        self.faceseg = FaceSeg()

    def run(self, nparray):
        image = nparray2Image(nparray)
        face_image = align_crop(image)
        face_mask = self.faceseg(face_image)

        face_image = cv2.resize(face_image, (256, 256), interpolation=cv2.INTER_AREA)
        face_mask = cv2.resize(face_mask, (256, 256))[:, :, np.newaxis] / 255.
        face = (face_image * face_mask + (1 - face_mask) * 255) / 127.5 - 1

        face = np.transpose(face[np.newaxis, :, :, :], (0, 3, 1, 2)).astype(np.float32)
        face = paddle.to_tensor(face)

        # inference
        with paddle.no_grad():
            cartoon = self.genA2B(face)[0][0]

        # post-process
        cartoon = np.transpose(cartoon.numpy(), (1, 2, 0))
        cartoon = (cartoon + 1) * 127.5
        cartoon = (cartoon * face_mask + (1 - face_mask) * 255).astype(np.uint8)
        return cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR), cv2.cvtColor(cartoon, cv2.COLOR_RGB2BGR)



p2c = Photo2CartoonPredictor()

def photo2Cartoon(image):
    return p2c.run(image)


if __name__ == '__main__':

    image = cv2.imread('./data/jaychou.jpeg')
    face_image, cartoon = photo2Cartoon(image)
    cv2.imwrite('./output/jaychou_source.jpg', face_image)
    cv2.imwrite('./output/jaychou_cartoon.jpg', cartoon)

    image = cv2.imread('./data/sunli.jpeg')
    face_image, cartoon = photo2Cartoon(image)
    cv2.imwrite('./output/sunli_source.jpg', face_image)
    cv2.imwrite('./output/sunli_cartoon.jpg', cartoon)
