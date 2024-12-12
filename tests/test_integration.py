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
        ports={"8080/tcp": 8080},
        volumes={
            os.path.abspath(os.path.join(os.getcwd(), "../ArdulinkProtocol")): {"bind": "/sketch", "mode": "ro"},
            "/dev/": {"bind": "/dev/", "mode": "rw"}
        },
        environment={ 
            "VIRTUALDEVICE": "/dev/ttyUSB0",
            "FILENAME": "ArdulinkProtocol.ino.hex"
        }
    )

    # print("Sleeping for 300 seconds to allow for manual intervention...")
    # time.sleep(300)

    ws_url = "ws://localhost:8080"
    retries = 0
    while retries < MAX_RETRIES:
        try:
            ws = websocket.create_connection(ws_url, timeout=2)  # Timeout for WebSocket connection
            print(f"Connected to WebSocket at {ws_url}")
            ws.close()
            break
        except Exception as e:
            print(f"WebSocket connection failed: {e}, retrying...")
            retries += 1
            time.sleep(2)

    if retries == MAX_RETRIES:
        pytest.fail(f"WebSocket connection to {ws_url} failed after {MAX_RETRIES} retries.")

    yield container

    print("Stopping Docker container...")
    container.stop()
    
    # Wait a little to ensure the container is fully stopped before removal
    time.sleep(2)
    
    try:
        container.remove(force=True)  # Force removal to handle any ongoing removal conflict
        print("Docker container removed successfully.")
    except docker.errors.APIError as e:
        print(f"Error during container removal: {e}")



@pytest.mark.timeout(30)
def test_wait_for_steady_message(docker_container):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        retries = 0
        while retries < MAX_RETRIES:
            ser.write("alp://notn/0/0?id=0\n".encode())
            serial_response = ser.readline().decode().strip()
            print(f"Raw serial response: {serial_response}")

            if serial_response == "alp://rply/ok?id=0":
                print(f"Received expected response: {serial_response}")
                return

            retries += 1
            time.sleep(RETRY_DELAY)
        
        pytest.fail(f"Expected response not received. Last response: {serial_response}")


@pytest.mark.timeout(30)
def test_can_switch_digital_pin(docker_container):
    ws_url = "ws://localhost:8080"
    ws = websocket.create_connection(ws_url, timeout=10)

    pin_mode_message = {
        "type": "pinMode",
        "pin": "D12",
        "mode": "digital"
    }

    print(f"Sending WebSocket message: {json.dumps(pin_mode_message)}")
    ws.send(json.dumps(pin_mode_message))

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        retries = 0
        while retries < MAX_RETRIES:
            ser.write("alp://notn/0/0?id=0\n".encode())
            serial_response = ser.readline().decode().strip()            
            print(f"Raw serial response: {serial_response}")

            if serial_response == "alp://rply/ok?id=0":
                print(f"Received expected response: {serial_response}")
                return

            retries += 1
            time.sleep(RETRY_DELAY)

        serial_message = "alp://ppsw/D12/1\n"
        print(f"Sending serial message: {serial_message}")
        ser.write(serial_message.encode())

        retries = 0
        expected_response = {
            "type": "pinState",
            "pin": "D12",
            "state": True
        }

        while retries < MAX_RETRIES:
            ws_response = ws.recv()
            print(f"Received WebSocket response: {ws_response}")
            try:
                ws_response_json = json.loads(ws_response)
                if ws_response_json == expected_response:
                    print(f"Received expected WebSocket response: {ws_response}")
                    return
            except json.JSONDecodeError:
                pass  # Ignore non-JSON responses
            
            retries += 1
            time.sleep(RETRY_DELAY)

        pytest.fail(f"Expected WebSocket response not received. Last response: {ws_response}")

    ws.close()
