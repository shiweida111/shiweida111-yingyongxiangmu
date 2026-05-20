import os
import base64
import json
from flask import Flask, request, jsonify, url_for, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback
from openai import OpenAI

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 20 * 1024 * 1024

OPENAI_API_KEY = "sk-vpofvhsboscvfihfizeolodxpdabdvgmvflovsgijljbooou"
model = 'Qwen/Qwen3.6-35B-A3B'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_prompt(category='deepfake'):
    prompts = {
        'gambling': "Analyze this image for gambling content including betting, odds, gambling tools and money transactions. Answer in Chinese.",
        'pornography': "Analyze this image for pornographic or inappropriate content. Answer in Chinese.",
        'deepfake': "Analyze this image to determine if it is AI-generated and provide detailed analysis reasons. Answer in Chinese.",
        'fraud': "请严格按照以下格式输出结果，不要使用任何Markdown格式（如**加粗**等）\n\n【一、风险评估】\n\n1. 诈骗可能性：[0-100%]\n2. 诈骗类型：[骗钱/涉黄/赌博/传销/仿冒/钓鱼/其他]\n3. 风险等级：[安全/低风险/中风险/高风险/极高风险]\n\n【二、界面内容识别】\n\n1. 界面顶部内容：[描述界面顶部的文字和布局]\n2. 界面主体内容：[描述界面主体区域]\n3. 界面底部内容：[描述界面底部区域]\n4. 其他特殊元素：[描述其他需要注意的元素]\n\n【三、风险要素识别】\n\n1. 高收益话术：[列出识别到的相关文字]\n2. 诱导性按钮：[列出识别到的按钮]\n3. 敏感操作：[列出识别到的敏感操作]\n4. 仿冒特征：[描述是否存在仿冒特征]\n\n【四、详细分析说明】\n\n[详细说明识别到的可疑点及判断依据]\n\n【五、安全建议】\n\n[针对识别结果给出具体安全建议]",
        'chat_fraud': "请严格按照以下格式输出结果，不要使用任何Markdown格式（如**加粗**等）\n\n【一、风险评估】\n\n1. 诈骗可能性：[0-100%]\n2. 诈骗类型：[骗钱/涉黄/赌博/传销/仿冒/钓鱼/其他]\n3. 风险等级：[安全/低风险/中风险/高风险/极高风险]\n\n【二、聊天记录识别】\n\n1. 聊天应用类型：[微信/QQ/抖音/微博/其他社交媒体]\n2. 发送方身份：[描述发送消息的一方身份，如客服、陌生人、熟人等]\n3. 接收方身份：[描述接收消息的一方身份]\n4. 对话主要内容：[概括对话的主要话题和目的]\n5. 关键聊天内容：[摘录关键的聊天内容]\n\n【三、风险要素识别】\n\n1. 诈骗话术特征：[识别到的典型诈骗话术]\n2. 情感操控手段：[识别到的情感操控手段，如激发紧迫感、恐惧感、同情心等]\n3. 金钱相关话题：[涉及转账、汇款、充值等相关内容]\n4. 个人信息索要：[是否存在索要个人敏感信息的行为]\n5. 可疑链接与附件：[是否存在可疑链接或附件]\n\n【四、详细分析说明】\n\n[详细说明识别到的可疑点及判断依据]\n\n【五、安全建议】\n\n[针对识别结果给出具体安全建议]"
    }
    return prompts.get(category, prompts['deepfake'])


def clean_result(text):
    import re
    if not isinstance(text, str):
        return text
    
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'^\s*\*\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*\*\s*$', '', text)
    text = re.sub(r'\s*\*\s*', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def analyze_image(image_path, prompt=None, stream=False):
    if prompt is None:
        prompt = get_prompt()
    
    try:
        client = OpenAI(base_url='https://api.siliconflow.cn/v1', api_key=OPENAI_API_KEY)
        
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"}},
                {"type": "text", "text": prompt}
            ]
        }]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4000,
            stream=stream
        )
        
        if stream:
            return response
        
        return response.choices[0].message.content
        
    except Exception as e:
        traceback.print_exc()
        return f"Analysis failed: {str(e)}"


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "success": True,
        "code": 200,
        "message": "Service is running",
        "data": {"timestamp": datetime.now().isoformat()}
    })


@app.route('/api/detect', methods=['POST'])
def detect_image():
    file = request.files.get('file')
    
    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "code": 400, "message": "Invalid file format", "data": None})
    
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return jsonify({"success": False, "code": 400, "message": "File size exceeds limit (max 20MB)", "data": None})
    file.seek(0)
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        result = analyze_image(filepath)
        
        if isinstance(result, str) and "failed" in result.lower():
            return jsonify({"success": False, "code": 500, "message": result, "data": None})
        
        cleaned_result = clean_result(result)
        result_text = "AI Generated" if ("AI generated" in result or "AI合成" in result or "deepfake" in result.lower() or "fake" in result.lower()) else "Real Image"
        
        return jsonify({
            "success": True,
            "code": 200,
            "message": "Detection completed",
            "data": {
                "detect_id": f"detect_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}",
                "result_text": result_text,
                "image_url": url_for('uploaded_file', filename=filename, _external=True),
                "detect_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "analysis_result": cleaned_result
            }
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "code": 500, "message": f"Detection failed: {str(e)}", "data": None})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    category = request.form.get('category')
    prompt = get_prompt(category or 'fraud')

    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "code": 400, "message": "Invalid file format", "data": None})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        result = analyze_image(filepath, prompt)

        if isinstance(result, str) and "failed" in result.lower():
            return jsonify({"success": False, "code": 500, "message": result, "data": None})

        cleaned_result = clean_result(result)

        return jsonify({
            "success": True,
            "code": 200,
            "message": "Analysis completed",
            "data": {
                "analyze_id": f"analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}",
                "analysis_result": cleaned_result,
                "image_url": url_for('uploaded_file', filename=filename, _external=True),
                "analyze_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "code": 500, "message": f"Analysis failed: {str(e)}", "data": None})


@app.route('/api/analyze/stream', methods=['POST'])
def analyze_stream():
    file = request.files.get('file')
    prompt = request.form.get('prompt') or get_prompt(request.form.get('category', 'deepfake'))
    
    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "code": 400, "message": "Invalid file format", "data": None})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    analyze_id = f"analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
    
    def generate():
        try:
            response = analyze_image(filepath, prompt, stream=True)
            
            if isinstance(response, str) and "failed" in response.lower():
                yield f"data: {json.dumps({'type': 'error', 'message': response})}\n\n"
                return
            
            full_result = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_result += content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content, 'full_result': full_result})}\n\n"
            
            cleaned_result = clean_result(full_result)
            final_data = json.dumps({
                'type': 'end',
                'full_result': cleaned_result,
                'analyze_id': analyze_id,
                'image_url': url_for('uploaded_file', filename=filename, _external=True),
                'analyze_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            yield f"data: {final_data}\n\n"
            
        except Exception as e:
            traceback.print_exc()
            error_data = json.dumps({'type': 'error', 'message': f'Analysis failed: {str(e)}'})
            yield f"data: {error_data}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port=5173)
