import time
import os
import docker
import serial
from websocket import create_connection
from websocket_listener import WebSocketListener
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for Serial Communication
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 20

# Function to get an unused serial port
def get_unused_serial_port(dev_prefix='/dev/ttyUSB'):
    existing_ports = [f for f in os.listdir('/dev') if f.startswith(dev_prefix)]
    existing_numbers = set(int(f[len(dev_prefix):]) for f in existing_ports)
    new_port_number = 0
    while new_port_number in existing_numbers:
        new_port_number += 1
    return f"{dev_prefix}{new_port_number}"

# Serial communication utility functions
def send_serial_message(ser, message, timeout=SERIAL_TIMEOUT):
    ser.write(f"{message}\n".encode())
    logger.info(f"Sent serial message: {message}")

def wait_for_serial_message(ser, expected_response, timeout=SERIAL_TIMEOUT):
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = ser.readline().decode().strip()
        logger.info(f"Received serial response: {response}")
        if response == expected_response:
            logger.info(f"Received expected serial response: {response}")
            return response
    raise RuntimeError(f"Expected serial response '{expected_response}' not received within {timeout} seconds.")

# Hook functions for Behave
def before_all(context):
    logger.info("Setting up test environment...")

    # Start Docker container
    client = docker.from_env()

    # Ensure SKETCH_FILE environment variable is set
    sketch_path = os.getenv("SKETCH_FILE")
    if not sketch_path:
        raise ValueError("Environment variable 'SKETCH_FILE' is not set.")
    
    sketch_dir, sketch_file = os.path.split(sketch_path)
    docker_image_tag = os.getenv("DOCKER_IMAGE_TAG", "latest")
    serial_port = get_unused_serial_port()

    try:
        context.container = client.containers.run(
            f"pfichtner/virtualavr:{docker_image_tag}",
            detach=True,
            auto_remove=False,
            ports={"8080/tcp": None},
            volumes={
                os.path.abspath(sketch_dir): {"bind": "/sketch", "mode": "ro"},
                "/dev/": {"bind": "/dev/", "mode": "rw"}
            },
            environment={
                "VIRTUALDEVICE": serial_port,
                "FILENAME": sketch_file,
                "DEVICEUSER": str(os.getuid())
            }
        )
        logger.info("Docker container started.")
    except docker.errors.DockerException as e:
        raise RuntimeError(f"Failed to start Docker container: {e}")

    # Wait for container to be ready and retrieve the dynamic port
    context.container.reload()
    ports = context.container.attrs['NetworkSettings']['Ports'].get('8080/tcp')
    if not ports or not ports[0].get('HostPort'):
        raise RuntimeError("Failed to retrieve the host port for the WebSocket connection.")
    host_port = ports[0]['HostPort']
    context.ws_url = f"ws://localhost:{host_port}"
    logger.info(f"WebSocket URL: {context.ws_url}")

    # Set up WebSocket connection with retries
    retry_count = 20
    retry_interval = 1

    for attempt in range(retry_count):
        try:
            context.ws = create_connection(context.ws_url, timeout=5)
            logger.info("WebSocket connection established.")
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{retry_count} failed: {e}")
            time.sleep(retry_interval)
            retry_interval = min(retry_interval * 2, 10)
    else:
        raise RuntimeError("Failed to establish WebSocket connection after retries.")

    # Start the WebSocket listener
    context.listener = WebSocketListener(context.ws)
    context.listener.start()
    logger.info("WebSocket listener started.")

    # Open the serial connection
    try:
        context.serial_conn = serial.Serial(
            port=serial_port,
            baudrate=SERIAL_BAUDRATE,
            timeout=SERIAL_TIMEOUT
        )
        logger.info(f"Serial connection established on {serial_port}.")
    except serial.SerialException as e:
        raise RuntimeError(f"Failed to open serial port {serial_port}: {e}")

def after_all(context):
    logger.info("Cleaning up test environment...")

    # Stop the WebSocket listener if it was started
    if getattr(context, 'listener', None):
        try:
            context.listener.stop()
            logger.info("WebSocket listener stopped.")
        except Exception as e:
            logger.error(f"Error stopping WebSocket listener: {e}")

    # Close WebSocket connection
    if getattr(context, 'ws', None):
        try:
            context.ws.close()
            logger.info("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"Error closing WebSocket connection: {e}")

    # Close the serial connection
    if getattr(context, 'serial_conn', None):
        try:
            context.serial_conn.close()
            logger.info("Serial connection closed.")
        except Exception as e:
            logger.error(f"Error closing serial connection: {e}")

    # Stop and remove Docker container
    if getattr(context, 'container', None):
        try:
            context.container.stop()
            context.container.remove(force=True)
            logger.info("Docker container stopped and removed successfully.")
        except Exception as e:
            logger.error(f"Error stopping/removing Docker container: {e}")
