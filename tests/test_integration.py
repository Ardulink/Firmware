import pytest
import docker
import websocket
import json
import time
import serial
import os

SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 5 
WS_TIMEOUT=5
MAX_RETRIES = 10
RETRY_DELAY = 1


DOCKER_IMAGE = "pfichtner/virtualavr"

@pytest.fixture(scope="module")
def docker_container():
    client = docker.from_env()

    print("Starting Docker container...")
    container = client.containers.run(
        DOCKER_IMAGE,
        detach=True,
        auto_remove=True,
        ports={"8080/tcp": None},  # Map container port to a random free port on the host
        volumes={
            os.path.abspath(os.path.join(os.getcwd(), "../ArdulinkProtocol")): {"bind": "/sketch", "mode": "ro"},
            "/dev/": {"bind": "/dev/", "mode": "rw"}
        },
        environment={ 
            "VIRTUALDEVICE": "/dev/ttyUSB0",
            "FILENAME": "ArdulinkProtocol.ino.hex"
        }
    )

    # Retrieve the dynamically assigned host port
    container.reload()  # Ensure latest state of the container
    host_port = container.attrs['NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']
    print(f"Docker container is running with WebSocket bound to host port {host_port}")

    ws_url = f"ws://localhost:{host_port}"
    retries = 0
    while retries < MAX_RETRIES:
        try:
            ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
            print(f"Connected to WebSocket at {ws_url}")
            ws.close()
            break
        except Exception as e:
            print(f"WebSocket connection failed: {e}, retrying...")
            retries += 1
            time.sleep(2)

    if retries == MAX_RETRIES:
        pytest.fail(f"WebSocket connection to {ws_url} failed after {MAX_RETRIES} retries.")

    yield container, ws_url

    print("Stopping Docker container...")
    container.stop()
    
    time.sleep(2)  # Allow some time for the container to fully stop
    
    try:
        container.remove(force=True)
        print("Docker container removed successfully.")
    except docker.errors.APIError as e:
        print(f"Error during container removal: {e}")


# Utility functions
def send_serial_message(ser, message, expected_response=None, retries=MAX_RETRIES, delay=RETRY_DELAY):
    """
    Send a serial message and optionally wait for an expected response.
    
    If no expected response is provided, the function will return immediately after sending.
    """
    for attempt in range(retries):
        ser.write(f"{message}\n".encode())
        if expected_response is None:
            print(f"Message sent: {message}")
            return

        response = ser.readline().decode().strip()
        print(f"Raw serial response: {response}")
        if response == expected_response:
            print(f"Received expected response: {response}")
            return response

        time.sleep(delay)

    if expected_response:
        pytest.fail(f"Expected response not received. Last response: {response}")
    return response


def send_ws_message(ws, message, expected_response=None, retries=MAX_RETRIES, delay=RETRY_DELAY):
    """
    Send a WebSocket message and optionally wait for an expected response.

    If no expected response is provided, the function returns immediately after sending.
    """
    ws.send(json.dumps(message))
    print(f"Sent WebSocket message: {json.dumps(message)}")

    if expected_response is None:
        # Return immediately if no expected response is specified
        print("No expected response specified, returning after sending.")
        return

    for attempt in range(retries):
        try:
            response = ws.recv()
            print(f"Received WebSocket response: {response}")
            response_json = json.loads(response)
            if response_json == expected_response:
                print(f"Received expected WebSocket response: {response}")
                return response_json
        except json.JSONDecodeError:
            print("Non-JSON WebSocket response received, ignoring.")
        except Exception as e:
            print(f"Error receiving WebSocket response: {e}")
        time.sleep(delay)

    pytest.fail(f"Expected WebSocket response not received.")


@pytest.mark.timeout(30)
def test_wait_for_steady_message(docker_container):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        send_serial_message(ser, "alp://notn/0/0?id=0", "alp://rply/ok?id=0")


@pytest.mark.timeout(30)
def test_can_switch_digital_pin_on_and_off(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
    send_ws_message(ws, {"type": "pinMode", "pin": "D12", "mode": "digital"})

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        send_serial_message(ser, "alp://ppsw/12/1")
        send_ws_message(ws, {}, {"type": "pinState", "pin": "D12", "state": True})

        send_serial_message(ser, "alp://ppsw/12/0")
        send_ws_message(ws, {}, {"type": "pinState", "pin": "D12", "state": False})

    ws.close()

@pytest.mark.timeout(30)
def test_can_set_values_on_analog_pin(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
    send_ws_message(ws, {"type": "pinMode", "pin": "D9", "mode": "analog"})

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        send_serial_message(ser, "alp://ppin/9/123")
        send_ws_message(ws, {}, {"type": "pinState", "pin": "D9", "state": 123})

        send_serial_message(ser, "alp://ppin/9/0")
        send_ws_message(ws, {}, {"type": "pinState", "pin": "D9", "state": 0})

    ws.close()
