import base64
from threading import Lock
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_socketio import SocketIO, Namespace
import eventlet
import numpy as np
import cv2

eventlet.monkey_patch()

from is_msgs.image_pb2 import Image
from is_wire.core import Subscription
from streamChannel import StreamChannel
import camera_controller as cc

app = Flask(__name__)
# app.secret_key = ''
socketio = SocketIO(app, async_mode='eventlet')


# --- Lógica de Streaming de Vídeo via WebSocket ---
thread_lock = Lock()
threads = {}

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        output_image = input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        output_image = cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    else:
        output_image = np.array([], dtype=np.uint8)
    return output_image

def video_stream_thread(cam_id, sid):
    global threads
    camera = cc.get_camera_by_id(cam_id)
    if not camera: return
    broker_uri, gateway_id = camera.get("broker_uri"), camera.get("gateway_id")
    topic = f"CameraGateway.{gateway_id}.Frame"
    channel = StreamChannel(uri=broker_uri)
    subscription = Subscription(channel=channel)
    subscription.subscribe(topic)
    print(f"Iniciando stream para Câmera ID {cam_id} no tópico {topic} para o cliente {sid}")
    while threads.get(sid) and threads[sid]['is_running']:
        try:
            msg = channel.consume_last()
            image = msg.unpack(Image)
            # image = to_np(image) # Não precisa transformar em um np.array
            base64_image = base64.b64encode(image.data).decode('utf-8')
            socketio.emit('video_frame', {'image': base64_image}, to=sid, namespace='/camera')
            socketio.sleep(0)
        except Exception as e:
            if "socket.timeout" not in str(e): print(f"Erro no stream da câmera {cam_id}: {e}")
            socketio.sleep(0.1)
    print(f"Parando stream para Câmera ID {cam_id} para o cliente {sid}")

class CameraStreamNamespace(Namespace):
    def on_connect(self):
        print(f"Cliente conectado: {request.sid}")
    def on_disconnect(self):
        print(f"Cliente desconectado: {request.sid}")
        global threads
        with thread_lock:
            if request.sid in threads:
                threads[request.sid]['is_running'] = False
    def on_start_stream(self, data):
        cam_id = data.get('cam_id')
        if not cam_id: return
        global threads
        with thread_lock:
            if request.sid in threads: threads[request.sid]['is_running'] = False
            thread = socketio.start_background_task(video_stream_thread, cam_id, request.sid)
            threads[request.sid] = {'thread': thread, 'is_running': True}

socketio.on_namespace(CameraStreamNamespace('/camera'))

# --- Rotas HTTP ---
@app.route('/')
def index():
    return render_template('index.html', cameras=cc.load_cameras())

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Registrar uma nova camera 
    if request.method == 'POST':
        name = request.form.get('name')
        broker_uri = request.form.get('broker_uri')
        gateway_id = int(request.form.get('gateway_id'))
        if not all([name, broker_uri, gateway_id]): # verificar se o usuario preencheu todos os campos
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('register'))
        # adicionar a nova camera no arquivo json
        cameras = cc.load_cameras()
        new_id = max([cam['id'] for cam in cameras] + [0]) + 1
        new_camera = {
            "id": new_id, "name": name, "broker_uri": broker_uri, "gateway_id": gateway_id
        }
        cameras.append(new_camera)
        cc.save_cameras(cameras)
        flash(f'Câmera "{name}" registrada com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html') # caso tenha sido o method GET

@app.route('/control/<int:cam_id>')
def control(cam_id):
    camera = cc.get_camera_by_id(cam_id)
    if not camera:
        flash(f'Câmera com ID {cam_id} não encontrada.', 'warning')
        return redirect(url_for('index'))
    return render_template('control.html', camera=camera)

# --- Endpoints da API ---
@app.route('/api/ptz_command', methods=['POST'])
def ptz_command():
    """Endpoint único para todos os comandos PTZ, incluindo zoom."""
    data = request.get_json()
    cam_id = data.get('cam_id')
    command = data.get('command')
    if not all([cam_id, command]):
        return jsonify({'status': 'error', 'message': 'Dados incompletos.'}), 400

    success, message = cc.send_ptz_command(cam_id, command)
    if success:
        return jsonify({'status': 'success', 'message': message})
    else:
        return jsonify({'status': 'error', 'message': message}), 500

@app.route('/api/delete_camera/<int:cam_id>', methods=['DELETE'])
def delete_camera_route(cam_id):
    """Endpoint para deletar uma câmera."""
    success = cc.delete_camera(cam_id)
    if success:
        return jsonify({'status': 'success', 'message': 'Câmera removida com sucesso.'})
    else:
        return jsonify({'status': 'error', 'message': 'Câmera não encontrada.'}), 404

@app.route('/api/get_camera_info/<int:cam_id>', methods=['GET'])
def get_camera_info(cam_id):
    """Endpoint para obter as informações PTZ atuais."""
    success, message, data = cc.get_current_ptz_info(cam_id)
    if success:
        return jsonify({'status': 'success', 'message': message, 'data': data})
    else:
        return jsonify({'status': 'error', 'message': message}), 500


if __name__ == '__main__':
    print("Iniciando servidor Flask-SocketIO...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
