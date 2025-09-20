import json
import socket
from is_msgs.camera_pb2 import CameraConfig, CameraConfigFields, PTZControl
from is_msgs.common_pb2 import FieldSelector
from is_wire.core import Message, Subscription, Logger
from streamChannel import StreamChannel

# Constantes
CAMERAS_DB_FILE = 'cameras.json'
REQUEST_TIMEOUT = 3.0  
PTZ_STEP = 50  # Define o step do movimento de pan/tilt e zoom
ZOOM_STEP = 5
# --- Funções de Gerenciamento de Câmera (cameras.json) ---
def load_cameras():
    try:
        with open(CAMERAS_DB_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_cameras(cameras):
    with open(CAMERAS_DB_FILE, 'w') as f:
        json.dump(cameras, f, indent=2)

def get_camera_by_id(cam_id):
    cameras = load_cameras()
    for cam in cameras:
        if cam.get('id') == cam_id:
            return cam
    return None

def delete_camera(cam_id):
    """Remove uma câmera da lista baseada no seu ID."""
    cameras = load_cameras()
    # Cria uma nova lista sem a câmera que tem o ID correspondente
    updated_cameras = [cam for cam in cameras if cam.get('id') != cam_id]
    
    # Verifica se alguma câmera foi realmente removida
    if len(updated_cameras) < len(cameras):
        save_cameras(updated_cameras)
        return True # Sucesso
    return False # Câmera não encontrada

# --- Funções de Comunicação ---
def _get_current_ptz_config(channel, subscription, gateway_id):
    topic = f"CameraGateway.{gateway_id}.GetConfig"
    selector = FieldSelector(fields=[CameraConfigFields.Value("ALL")])
    channel.publish(Message(content=selector, reply_to=subscription), topic=topic)
    try:
        reply = channel.consume(timeout=REQUEST_TIMEOUT)
        config = reply.unpack(CameraConfig)
        return {
            "x": config.ptzcontrol.absolute.x,
            "y": config.ptzcontrol.absolute.y,
            "z": config.ptzcontrol.absolute.z
        }
    except socket.timeout:
        log = Logger(name="PTZ-Controller")
        log.warn(f"Timeout ao obter config da câmera {gateway_id}. Tópico: {topic}")
        return None
    except Exception as e:
        log = Logger(name="PTZ-Controller")
        log.error(f"Erro ao obter config da câmera {gateway_id}: {e}")
        return None

def _send_ptz_absolute_position(channel, subscription, gateway_id, x, y, z):
    log = Logger(name="PTZ-Controller")
    topic = f"CameraGateway.{gateway_id}.SetConfig"
    config = CameraConfig()
    config.ptzcontrol.absolute.x = x
    config.ptzcontrol.absolute.y = y
    config.ptzcontrol.absolute.z = z
    msg_set_ptz = Message(content=config, reply_to=subscription)
    channel.publish(msg_set_ptz, topic)
    log.info(f"Comando PTZ enviado para Câmera {gateway_id}: x={x}, y={y}, z={z}")

def get_current_ptz_info(cam_id):
    """Busca e retorna as coordenadas PTZ atuais de uma câmera."""
    camera = get_camera_by_id(cam_id)
    if not camera:
        return False, "Câmera não encontrada.", None

    broker_uri = camera.get("broker_uri")
    gateway_id = camera.get("gateway_id")
    
    try:
        channel = StreamChannel(uri=broker_uri)
        subscription = Subscription(channel)
        
        current_pos = _get_current_ptz_config(channel, subscription, gateway_id)
        if current_pos is None:
            return False, "Não foi possível obter a posição atual da câmera.", None
        
        return True, "Informações obtidas com sucesso.", current_pos

    except Exception as e:
        log = Logger(name="PTZ-Info")
        log.error(f"Falha ao obter informações da câmera {cam_id}: {e}")
        return False, f"Erro de comunicação com o broker: {e}", None

# --- Função Principal de Controle ---
def send_ptz_command(cam_id, command):
    """
    Função ÚNICA para todos os comandos: PAN, TILT e ZOOM (com botões).
    """
    camera = get_camera_by_id(cam_id)
    if not camera:
        return False, "Câmera não encontrada."

    broker_uri = camera.get("broker_uri")
    gateway_id = camera.get("gateway_id")
    
    try:
        channel = StreamChannel(uri=broker_uri)
        subscription = Subscription(channel)
        
        if command == 'home':
            # Obtém apenas o zoom atual para não resetá-lo
            current_pos = _get_current_ptz_config(channel, subscription, gateway_id)
            current_zoom = current_pos['z'] if current_pos else 0
            _send_ptz_absolute_position(channel, subscription, gateway_id, 0, 0, current_zoom)
            return True, "Câmera movida para a posição inicial."

        
        current_pos = _get_current_ptz_config(channel, subscription, gateway_id)
        if current_pos is None:
            return False, "Não foi possível obter a posição atual da câmera."
            
        x, y, z = current_pos['x'], current_pos['y'], current_pos['z']
        
        # Calcula a nova posição baseada no comando
        if command == 'pan_left':
            x -= PTZ_STEP
        elif command == 'pan_right':
            x += PTZ_STEP
        elif command == 'tilt_up':
            y -= PTZ_STEP
        elif command == 'tilt_down':
            y += PTZ_STEP
        elif command == 'zoom_in':
            z += ZOOM_STEP
        elif command == 'zoom_out':
            z -= ZOOM_STEP
        else:
            return False, "Comando PTZ inválido."

        _send_ptz_absolute_position(channel, subscription, gateway_id, x, y, z)
        return True, "Comando enviado com sucesso."

    except Exception as e:
        log = Logger(name="PTZ-Controller")
        log.critical(f"Falha na comunicação com a câmera {cam_id}: {e}")
        return False, f"Erro de comunicação com o broker: {e}"
