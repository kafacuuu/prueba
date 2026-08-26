import os
import tempfile
import subprocess
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/process-vertical', methods=['POST'])
def process_vertical():
    if 'file' not in request.files:
        return {"status": "error", "message": "No se encontró ningún archivo"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"status": "error", "message": "Nombre de archivo vacío"}, 400

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.mp4")
    output_path = os.path.join(temp_dir, "output.mp4")
    
    file.save(input_path)

    try:
        # FFmpeg optimizado con preset ultrafast para evitar timeouts y 502 en Render
        command = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'copy',
            output_path
        ]
        
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return send_file(output_path, as_attachment=True, download_name="vertical.mp4")

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error al procesar FFmpeg: {e.stderr.decode()}"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
