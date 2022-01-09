# _*_ coding: utf-8 _*_

import os
import json
from docx import Document
from baidufanyi import texttrans

def translateStatement(s, appid, appkey):
    response = texttrans(s, appid, appkey)
    if (not hasattr(response, 'error')):
        text = json.loads(response.text)
        results = text['result']['trans_result']
        translated = ''
        for result in results:
            translated = translated + result['dst']
        return translated
    else:
        return ''

def translateFile(file, appid, appkey):
    document = Document(file)
    for num, paragraph in enumerate(document.paragraphs):
        # Read paragraph text
        source_text = paragraph.text.strip()
        if source_text:
            lines = paragraph.runs
            if lines:
                for li, line in enumerate(lines):
                    temp = lines[li].text
                    lines[li].text = temp.replace(temp, '')
                translated = translateStatement(source_text, appid, appkey)
                lines[0].text = translated
    document.save(file + 'translated.docx')

if __name__ == '__main__':
    appid='Z2S7BV5GNhwBpBPGtjGrpyxf'
    appkey='uVpGB27MtCGnAF2AxcZYTFYks1SS1Pss'
    # print(translateStatement('随便说点什么吧，测试测试', appid, appkey))
    translateFile('C:\\Users\\fengfan_zheng\\Desktop\\用户手册.docx', appid, appkey)
    