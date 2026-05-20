"""
诈骗软件识别 - Web 服务
提供网页界面，方便普通民众使用
"""

import os
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename
from scam_detector import ScamDetector
from report_generator import generate_report

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'scam_uploads'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp', 'jfif'}
ALLOWED_CONTENT_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/bmp',
    'image/webp',
    'image/jfif',
    'image/x-ms-bmp'
}


def allowed_file(filename, content_type=None):
    # 方法1：检查文件名扩展名
    if filename and '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in ALLOWED_EXTENSIONS:
            return True
    
    # 方法2：检查 MIME 类型（适用于没有扩展名的文件）
    if content_type and content_type in ALLOWED_CONTENT_TYPES:
        return True
    
    # 方法3：检查 content_type 是否包含 image（通用检查）
    if content_type and content_type.startswith('image/'):
        return True
    
    return False


@app.route('/')
def index():
    return render_template('scam_checker.html')


@app.route('/check', methods=['POST'])
def check_scam():
    file = request.files.get('screenshot')
    user_desc = request.form.get('description', '').strip()

    if not file:
        return jsonify({
            "success": False,
            "error": "请上传图片文件"
        })

    filename = file.filename
    content_type = file.content_type
    
    if not allowed_file(filename, content_type):
        return jsonify({
            "success": False,
            "error": "请上传有效的图片文件（png, jpg, jpeg, bmp, webp）"
        })

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    file.save(filepath)

    try:
        detector = ScamDetector()
        result = detector.analyze_screenshot(filepath, user_desc if user_desc else None)

        # 检查分析是否成功
        if not result.get("success", False):
            return jsonify({
                "success": False,
                "error": result.get("error", "分析失败")
            })

        # 检查是否有 result 字段
        if "result" not in result:
            return jsonify({
                "success": False,
                "error": "未获取到分析结果"
            })

        return jsonify({
            "success": True,
            "result": result["result"],
            "image_url": url_for('uploaded_file', filename=filename)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/generate_report', methods=['POST'])
def gen_report():
    data = request.get_json()
    image_path = data.get('image_path')
    analysis_result = data.get('analysis_result')
    user_desc = data.get('user_description')
    report_format = data.get('format', 'txt')

    if not image_path or not analysis_result:
        return jsonify({
            "success": False,
            "error": "缺少必要参数"
        })

    try:
        report_data = {
            "success": True,
            "result": analysis_result
        }
        report_path = generate_report(
            image_path,
            report_data,
            user_desc,
            report_format
        )

        report_filename = os.path.basename(report_path)

        return jsonify({
            "success": True,
            "report_url": url_for('download_report', filename=report_filename),
            "report_filename": report_filename
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/download_report/<filename>')
def download_report(filename):
    return send_from_directory('reports', filename, as_attachment=True)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    print("=" * 50)
    print("  [SCAM DETECTOR] Web Service")
    print("  URL: http://127.0.0.1:5174")
    print("=" * 50)
    app.run(debug=False, port=5174)