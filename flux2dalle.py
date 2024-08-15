# -*- coding: utf-8 -*-
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 直接在代码中设置FAL_KEY
FAL_KEY = "your_fal_key_here"  # 请将这里的 "your_fal_key_here" 替换为你的实际FAL_KEY

@app.route('/v1/images/generations', methods=['POST'])
def generate_image():
    data = request.json
    
    # 从 DALL-E 格式的请求中提取参数
    prompt = data.get('prompt', '')
    n = data.get('n', 1)  # DALL-E 支持生成多张图片，但 Flux Pro 只支持一张
    size = data.get('size', '1024x1024')  # DALL-E 的默认尺寸
    
    # 将 DALL-E 的尺寸转换为 Flux Pro 支持的尺寸
    if size == '1024x1024':
        width, height = 1024, 1024
    elif size == '512x512':
        width, height = 512, 512
    else:
        width, height = 1024, 768  # Flux Pro 的默认尺寸
    
    # 构建 Flux Pro 的请求
    flux_data = {
        "prompt": prompt,
        "width": width,
        "height": height
    }
    
    # 发送请求到 Flux Pro
    response = requests.post(
        'https://fal.run/fal-ai/flux-pro',
        headers={
            'Authorization': 'Key {}'.format(FAL_KEY),
            'Content-Type': 'application/json'
        },
        json=flux_data
    )
    
    if response.status_code == 200:
        flux_response = response.json()
        
        # 获取图片 URL
        image_url = flux_response['images'][0]['url']
        
        # 构建 DALL-E 格式的响应
        dalle_response = {
            "created": int(time.time()),
            "data": [{
                "url": image_url
            }]
        }
        
        return jsonify(dalle_response), 200
    else:
        return jsonify({"error": {"message": "Failed to generate image"}}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
