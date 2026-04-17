import os
import socket
from flask import Flask, request, render_template, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
from db import init_db, generate_code, save_file, get_file_by_code, increment_downloads

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

def human_size(nbytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # this isn't actually connecting, just routing to determine local interface IP :)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    original_name = secure_filename(f.filename)
    if not original_name:
        original_name = "file"
        
    code = generate_code()
    ext = os.path.splitext(original_name)[1]
    stored_name = f"{code}{ext}"
    f.save(os.path.join(UPLOAD_DIR, stored_name))

    size = os.path.getsize(os.path.join(UPLOAD_DIR, stored_name))
    mimetype = f.content_type or 'application/octet-stream'

    save_file(stored_name, original_name, code, size, mimetype)


    share_url_host = request.host_url.rstrip('/') + f'/f/{code}'
    

    local_ip = get_local_ip()
    port = request.environ.get('SERVER_PORT', '5000')
    scheme = request.scheme
    share_url_local = f"{scheme}://{local_ip}:{port}/f/{code}"

    return jsonify({
        'code': code,
        'url_host': share_url_host,
        'url_local': share_url_local,
        'name': original_name,
        'size': human_size(size)
    })

@app.route('/f/<code>')
def file_page(code):
    file_info = get_file_by_code(code)
    if not file_info:
        abort(404)
    file_info['human_size'] = human_size(file_info['size'])
    return render_template('download.html', file=file_info)

@app.route('/download/<code>')
def download(code):
    file_info = get_file_by_code(code)
    if not file_info:
        abort(404)
    increment_downloads(code)
    return send_from_directory(UPLOAD_DIR, file_info['filename'], as_attachment=True,
                                download_name=file_info['original_name'])

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)
