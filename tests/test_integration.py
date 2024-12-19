import pytest
import docker
from collections import deque
import threading
import queue
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

class WebSocketListener:
    def __init__(self, ws):
        """
        Initialize the WebSocketListener with the WebSocket connection
        :param ws: WebSocket object
        """
        self.ws = ws
        self.queue = queue.Queue()
        self.running = True

    def start(self):
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def _listen(self):
        while self.running:
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                print(f"Background listener received: {parsed_message}")
                self.queue.put(parsed_message)
            except Exception as e:
                print(f"Error in WebSocket listener: {e}")
                self.running = False

    def stop(self):
        self.running = False
        self.thread.join()

    def get_message(self, timeout=None):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_all_messages(self):
        """
        Retrieve all messages from the queue without removing them.
        Returns a list of messages in the queue.
        """
        return list(self.queue.queue)  # Return a copy of the current messages in the queue


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
    yield ws_url

    print("Stopping and removing Docker container...")
    container.remove(force=True)


@pytest.fixture
def ws_listener(docker_container):
    """
    Starts a global WebSocket listener after the Docker container is ready.
    Retries connection until the WebSocket server is reachable.
    """
    ws_url = docker_container

    # Retry connection to WebSocket
    for _ in range(20):
        try:
            ws = websocket.create_connection(ws_url, timeout=5)
            print(f"WebSocket connection established to {ws_url}")
            break
        except Exception as e:
            print(f"Retrying WebSocket connection: {e}")
            time.sleep(1)
    else:
        pytest.fail("Failed to establish WebSocket connection after retries")

    # Start the WebSocket listener
    listener = WebSocketListener(ws)
    listener.start()

    yield listener

    # Stop the listener and close the WebSocket
    listener.stop()
    ws.close()


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


def send_ws_message(listener, message, timeout=WS_TIMEOUT):
    listener.ws.send(json.dumps(message))
    print(f"Sent WebSocket message: {json.dumps(message)}")


def wait_for_ws_message(listener, pin, expected_state, timeout=WS_TIMEOUT):
    """
    Check the last message of a specific pin in the WebSocket listener's buffer.
    If it does not match or no message for the pin is found, wait for it until the timeout.

    Args:
        listener: The WebSocket listener instance.
        pin: The pin to look for in the messages.
        expected_state: The expected state of the pin.
        timeout: The maximum time to wait for the message.

    Raises:
        AssertionError: If the expected state for the pin is not received within the timeout.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        # Filter messages related to the specified pin
        pin_messages = [msg for msg in listener.get_all_messages() if msg.get("pin") == pin]

        if pin_messages:
            last_message = pin_messages[-1]
            if last_message.get("state") == expected_state:
                print(f"Last message for pin {pin} has the expected state: {expected_state}")
                return last_message

        time.sleep(0.1)

    pytest.fail(f"No message for pin {pin} with the expected state {expected_state} received within {timeout} seconds.")


def set_pin_mode(ws, pin, mode):
    """
    Sets the (listening) mode of a pin via WebSocket.
    """
    send_ws_message(ws, {"type": "pinMode", "pin": pin, "mode": mode})


def pin_state(pin, state):
    return {"type": "pinState", "pin": pin, "state": state}


def set_pin_state(ws, pin, state):
    """
    Sets the state of a pin via WebSocket.
    """
    send_ws_message(ws, pin_state(pin, state))


def wait_for_steady_state(ser):
    """
    Ensure the serial connection is in a steady state by sending a specific notification
    and waiting for the expected acknowledgment.
    """
    send_serial_message(ser, "alp://notn/0/0?id=0")
    wait_for_serial_message(ser, "alp://rply/ok?id=0")


def test_wait_for_steady_message(ws_listener):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
                wait_for_steady_state(ser)


def test_can_switch_digital_pin_on_and_off(ws_listener):
    set_pin_mode(ws_listener, "D12", "digital")

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://ppsw/12/1")
        wait_for_ws_message(ws_listener, "D12", True)

        send_serial_message(ser, "alp://ppsw/12/0")
        wait_for_ws_message(ws_listener, "D12", False)


def test_can_set_values_on_analog_pin(ws_listener):
    set_pin_mode(ws_listener, "D9", "analog")

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://ppin/9/123")
        wait_for_ws_message(ws_listener, "D9", 123)

        send_serial_message(ser, "alp://ppin/9/0")
        wait_for_ws_message(ws_listener, "D9", 0)


def test_tone_without_rply_message(ws_listener):
    set_pin_mode(ws_listener, "D9", "analog")

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://tone/9/123/-1")
        wait_for_ws_message(ws_listener, "D9", 127)

        send_serial_message(ser, "alp://notn/9")
        wait_for_ws_message(ws_listener, "D9", 0)


def test_tone_with_rply_message(ws_listener):
    set_pin_mode(ws_listener, "D9", "analog")

    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://tone/9/123/-1?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_ws_message(ws_listener, "D9", 127)

        send_serial_message(ser, "alp://notn/9?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")

        wait_for_ws_message(ws_listener, "D9", 0)


def test_custom_messages_are_not_supported_in_default_implementation(ws_listener):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://cust/abc/xyz?id=42")
        wait_for_serial_message(ser, "alp://rply/ko?id=42")


def test_unknown_command_result_in_ko_rply(docker_container):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://XXXX/123/abc/X-Y-Z?id=42")
        wait_for_serial_message(ser, "alp://rply/ko?id=42")


def test_can_read_analog_pin_state_initial_pin_state_0(ws_listener):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://srla/5?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://ared/5/0")
        set_pin_state(ws_listener, "A5", 987)
        wait_for_serial_message(ser, "alp://ared/5/987")
        send_serial_message(ser, "alp://spla/5?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")


def test_can_read_analog_pin_state_initial_pin_state_987(ws_listener):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        set_pin_state(ws_listener, "A5", 987)
        send_serial_message(ser, "alp://srla/5?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://ared/5/987")
        send_serial_message(ser, "alp://spla/5?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")


def test_can_read_digital_pin_state_initial_pin_state_0(ws_listener):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        send_serial_message(ser, "alp://srld/12?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://dred/12/0")
        set_pin_state(ws_listener, "D12", True)
        wait_for_serial_message(ser, "alp://dred/12/1")
        send_serial_message(ser, "alp://spld/12?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")


def test_can_read_digital_pin_state_initial_pin_state_1(ws_listener):
    with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
        wait_for_steady_state(ser)

        set_pin_state(ws_listener, "D12", True)
        send_serial_message(ser, "alp://srld/12?id=42")
        wait_for_serial_message(ser, "alp://rply/ok?id=42")
        wait_for_serial_message(ser, "alp://dred/12/1")
        send_serial_message(ser, "alp://spld/12?id=43")
        wait_for_serial_message(ser, "alp://rply/ok?id=43")
