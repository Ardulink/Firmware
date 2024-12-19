import pytest
import docker
import websocket
import json
import time
import serial
import os

def get_unused_serial_port(dev_prefix='/dev/ttyUSB'):
    # List all devices that match the given prefix (e.g., /dev/ttyUSB0, /dev/ttyUSB1, etc.)
    existing_ports = [f for f in os.listdir('/dev') if f.startswith(dev_prefix)]
    
    # Extract the numbers from the existing port names
    existing_numbers = set(int(f[len(dev_prefix):]) for f in existing_ports)
    
    # Find the first unused number (you could also generate a random number here)
    new_port_number = 0
    while new_port_number in existing_numbers:
        new_port_number += 1
    
    # Return the full path to the first unused serial port
    return f"{dev_prefix}{new_port_number}"

SERIAL_PORT = get_unused_serial_port()
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 20
WS_TIMEOUT=20


@pytest.fixture
def docker_container():
    client = docker.from_env()

    print("Starting Docker container...")
    container = client.containers.run(
        "pfichtner/virtualavr",
        detach=True,
        auto_remove=True,
        ports={"8080/tcp": None},  # Map container port to a random free port on the host
        volumes={
            os.path.abspath(os.path.join(os.getcwd(), "ArdulinkProtocol")): {"bind": "/sketch", "mode": "ro"},
            "/dev/": {"bind": "/dev/", "mode": "rw"}
        },
        environment={ 
            "VIRTUALDEVICE": SERIAL_PORT,
            "FILENAME": "ArdulinkProtocol.ino",
            "DEVICEUSER": str(os.getuid())
        }
    )

    # Retrieve the dynamically assigned host port
    container.reload()  # Ensure latest state of the container
    host_port = container.attrs['NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']
    print(f"Docker container is running with WebSocket bound to host port {host_port}")

    ws_url = f"ws://localhost:{host_port}"
    retries = 0
    while retries < 20:
        try:
            ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
            print(f"Connected to WebSocket at {ws_url}")
            ws.close()
            break
        except Exception as e:
            print(f"WebSocket connection failed: {e}, retrying...")
            retries += 1
            time.sleep(1)

    if ws is None:
        pytest.fail(f"WebSocket connection to {ws_url} failed.")

    yield container, ws_url

    print("Stopping and removing Docker container...")
    try:
        container.remove(force=True)
        print("Docker container stopped and removed successfully.")
    except docker.errors.APIError as e:
        print(f"Error during container stop/removal: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def send_serial_message(ser, message, timeout=SERIAL_TIMEOUT):
    ser.write(f"{message}\n".encode())
    print(f"Sent serial message: {message}")


def wait_for_serial_message(ser, expected_response, timeout=SERIAL_TIMEOUT):
    start_time = time.time()  # Record the start time

    while time.time() - start_time < timeout:
        response = ser.readline().decode().strip()  # Will block for `ser.timeout` seconds
        print(f"Received serial response: {response}")

        if response == expected_response:
            print(f"Received expected serial response: {response}")
            return response

    pytest.fail(f"Expected serial response '{expected_response}' not received within {timeout} seconds.")


def send_ws_message(ws, message, timeout=WS_TIMEOUT):
    ws.send(json.dumps(message))
    print(f"Sent WebSocket message: {json.dumps(message)}")


def wait_for_ws_message(ws, expected_response, timeout=WS_TIMEOUT):
    start_time = time.time()  # Record the start time

    while time.time() - start_time < timeout:
        try:
            response = ws.recv()
            print(f"Received WebSocket response: {response}")
            response_json = json.loads(response)

            if response_json == expected_response:
                print(f"Received expected WebSocket response: {response_json}")
                return response_json
        except json.JSONDecodeError:
            print("Non-JSON WebSocket response received, ignoring.")
        except Exception as e:
            print(f"Error receiving WebSocket response: {e}")

    pytest.fail(f"Expected WebSocket response '{expected_response}' not received within {timeout} seconds.")


def wait_for_steady_state(ser):
    """
    Ensure the serial connection is in a steady state by sending a specific notification
    and waiting for the expected acknowledgment.
    """
    send_serial_message(ser, "alp://notn/0/0?id=0")
    wait_for_serial_message(ser, "alp://rply/ok?id=0")


def test_wait_for_steady_message(docker_container):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
                wait_for_steady_state(ser)


def test_can_switch_digital_pin_on_and_off(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
    send_ws_message(ws, {"type": "pinMode", "pin": "D12", "mode": "digital"})

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://ppsw/12/1")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D12", "state": True})

        send_serial_message(ser, "alp://ppsw/12/0")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D12", "state": False})

    ws.close()


def test_can_set_values_on_analog_pin(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
    send_ws_message(ws, {"type": "pinMode", "pin": "D9", "mode": "analog"})

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://ppin/9/123")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D9", "state": 123})

        send_serial_message(ser, "alp://ppin/9/0")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D9", "state": 0})

    ws.close()


def test_tone_without_rply_message(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
    send_ws_message(ws, {"type": "pinMode", "pin": "D9", "mode": "analog"})

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://tone/9/123/-1")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D9", "state": 127})

        send_serial_message(ser, "alp://notn/9")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D9", "state": 0})

    ws.close()


def test_tone_with_rply_message(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)
    send_ws_message(ws, {"type": "pinMode", "pin": "D9", "mode": "analog"})

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://tone/9/123/-1?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_ws_message(ws, {"type": "pinState", "pin": "D9", "state": 127})

        send_serial_message(ser, "alp://notn/9?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")

        wait_for_ws_message(ws, {"type": "pinState", "pin": "D9", "state": 0})

    ws.close()


def test_custom_messages_are_not_supported_in_default_implementation(docker_container):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://cust/abc/xyz?id=42")
        wait_for_serial_message(ser, "alp://rply/ko?id=42")


def test_unknown_command_result_in_ko_rply(docker_container):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://XXXX/123/abc/X-Y-Z?id=42")
        wait_for_serial_message(ser, "alp://rply/ko?id=42")


def test_can_read_analog_pin_state_initial_pin_state_0(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://srla/5?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://ared/5/0")
        send_ws_message(ws, {"type": "pinState", "pin": "A5", "state": 987})
        wait_for_serial_message(ser, "alp://ared/5/987")
        send_serial_message(ser, "alp://spla/5?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")

    ws.close()


def test_can_read_analog_pin_state_initial_pin_state_987(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_ws_message(ws, {"type": "pinState", "pin": "A5", "state": 987})
        send_serial_message(ser, "alp://srla/5?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://ared/5/987")
        send_serial_message(ser, "alp://spla/5?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")

    ws.close()


def test_can_read_digital_pin_state_initial_pin_state_0(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://srld/12?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://dred/12/0")
        send_ws_message(ws, {"type": "pinState", "pin": "D12", "state": True})
        wait_for_serial_message(ser, "alp://dred/12/1")
        send_serial_message(ser, "alp://spld/12?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")

    ws.close()


def test_can_read_digital_pin_state_initial_pin_state_1(docker_container):
    container, ws_url = docker_container
    ws = websocket.create_connection(ws_url, timeout=WS_TIMEOUT)

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_ws_message(ws, {"type": "pinState", "pin": "D12", "state": True})
        send_serial_message(ser, "alp://srld/12?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://dred/12/1")
        send_serial_message(ser, "alp://spld/12?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")

    ws.close()
