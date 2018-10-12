#!/usr/bin/env python
# coding=utf-8

import os

from flask import Flask, request, Response, render_template,jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('./index.html')


@app.route('/checkChunk', methods=['POST'])
def checkChunk():
    return jsonify({'ifExist':False})


@app.route('/mergeChunks', methods=['POST'])
def mergeChunks():
    fileName=request.form.get('fileName')
    print fileName
    md5=request.form.get('fileMd5')
    chunk = 0  # 分片序号
    with open(u'./upload/{}'.format(fileName), 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = './upload/{}-{}'.format(md5, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except IOError, msg:
                break
            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间
    return jsonify({'upload':True})


@app.route('/upload', methods=['POST'])
def upload():  # 接收前端上传的一个分片
    md5=request.form.get('fileMd5')
    chunk_id=request.form.get('chunk',0,type=int)
    filename = '{}-{}'.format(md5,chunk_id)
    upload_file = request.files['file']
    upload_file.save('./upload/{}'.format(filename))
    return jsonify({'upload_part':True})



@app.route('/file/list', methods=['GET'])
def file_list():
    files = os.listdir('./upload/')  # 获取文件目录
    files = map(lambda x: x if isinstance(x, unicode) else x.decode('utf-8'), files)  # 注意编码
    return render_template('./list.html', files=files)


@app.route('/file/download/<filename>', methods=['GET'])
def file_download(filename):
    def send_chunk():  # 流式读取
        store_path = './upload/%s' % filename
        with open(store_path, 'rb') as target_file:
            while True:
                chunk = target_file.read(20 * 1024 * 1024)
                if not chunk:
                    break
                yield chunk

    return Response(send_chunk(), content_type='application/octet-stream')


if __name__ == '__main__':
    app.run(debug=False, threaded=True)
