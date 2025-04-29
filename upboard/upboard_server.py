#! python
# -*- coding: utf-8 -*-

import os
import argparse
from functools import wraps
from flask import Flask, send_from_directory, abort, request, jsonify
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, ALL
from waitress import serve

def create_app(base_dir='assets', password=None):
    app = Flask(__name__)
    app.config['UPLOAD_PASSWORD'] = password
    app.config['UPLOADED_FILES_DEST'] = os.path.abspath(os.path.join(base_dir, 'RELEASES'))
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
    files = UploadSet('files', ALL)
    configure_uploads(app, files)

    def auth_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not app.config['UPLOAD_PASSWORD']:
                return f(*args, **kwargs)
                
            auth = request.headers.get('Authorization')
            if not auth or auth != app.config['UPLOAD_PASSWORD']:
                return jsonify({'error': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/api/v1/releases/<product>/<platform>/<arch>/<filename>', methods=['PUT'])
    @app.route('/api/v1/releases/<product>/<platform>/<arch>/<version>/<filename>', methods=['PUT'])
    @auth_required
    def releases(product, platform, arch, filename, version=None):
        filename = secure_filename(filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400

        save_dir = os.path.join(product, platform, arch)
        if version:
            save_dir = os.path.join(save_dir, version)
        
        try:
            file_storage = request.files.get('file')
            if not file_storage:
                return jsonify({'error': 'No file part in request'}), 400
            
            # 检查文件是否存在
            oldfile = os.path.join(app.config['UPLOADED_FILES_DEST'], save_dir, filename)
            if os.path.exists(oldfile):
                os.remove(oldfile)

            # 保存文件（自动创建目录）
            saved_filename = files.save(
                file_storage,
                folder=save_dir,
                name=filename
            )

            saved_filename = saved_filename.replace(os.path.sep, '/')
            return jsonify({
                'message': 'File uploaded successfully',
                'path': saved_filename,
                'url': '/api/v1/update/' + saved_filename,
            }), 201

        except Exception as e:
            return jsonify({
                'error': str(e),
                'details': 'Upload failed'
            }), 500

    @app.route('/api/v1/updates/<product>/<platform>/<arch>/<version>/<filename>')
    def updates(product, platform, arch, version, filename):
        direcory = app.config['UPLOADED_FILES_DEST']

        # 先尝试带版本号的路径
        version_path = os.path.join(direcory, product, platform, arch, version, filename)
        if os.path.exists(version_path):
            return send_from_directory(os.path.join(direcory, product, platform, arch, version), filename)
        
        # 如果带版本号的路径不存在，尝试不带版本号的路径
        no_version_path = os.path.join(direcory, product, platform, arch, filename)
        if os.path.exists(no_version_path):
            return send_from_directory(os.path.join(direcory, product, platform, arch), filename)
        
        abort(404)

    return app

def main():
    parser = argparse.ArgumentParser(description='UpBoard - Lightweight Software Update Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on (default: 5000)')
    parser.add_argument('--dir', default='.', help='Base directory for releases (default: current directory)')
    parser.add_argument('--password', help='Password for publish API (optional)')
    args = parser.parse_args()

    if not os.path.exists(args.dir):
        os.makedirs(args.dir, exist_ok=True)
        print(f"Created base directory: {os.path.abspath(args.dir)}")

    app = create_app(args.dir, args.password)

    print(f"Serving files from: {os.path.abspath(args.dir)}")
    print(f"Server running on http://{args.host}:{args.port}")
    print("GET /api/v1/updates/<product>/<platform>/[<version>/]<filename>")
    print("PUT /api/v1/releases/<product>/<platform>/[<version>/]<filename>")
    print("PUT: curl -X PUT -H 'Authorization: admin' -F  file=@RELEASES\\\n"
          "     http://host:port/api/v1/releases/vlocation/win32/x64/1.0.0-alpha2/RELEASES")
    if args.password:
        print("Publish API authentication is ENABLED")
    else:
        print("Publish API authentication is DISABLED")
    print("Press Ctrl+C to quit")

    if app.config.get("ENV", "production") == "development":
        app.run(host=args.host, port=args.port, debug=True)
    else:
        serve(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()
