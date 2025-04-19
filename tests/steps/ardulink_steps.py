from behave import given, when, then
import json
import time
import re
import uuid
from websocket_listener import WebSocketListener

def parse_value(value):
    if value.lower() in ("true", "false", "on", "off", "high", "low"):
        return value.lower() == "true" or value.lower() == "on" or value.lower() == "high"
    return int(value)


def send_ws_message(ws, message):
    reply_id = str(uuid.uuid4())
    message["replyId"] = reply_id
    ws.send(json.dumps(message))
    print(f"Sent WebSocket message: {json.dumps(message)}")
    return reply_id


def wait_for_reply(listener, reply_id, timeout=20):
    start_time = time.time()
    while time.time() - start_time < timeout:
        messages = listener.get_all_messages()
        for msg in messages:
            if msg.get("replyId") == reply_id and msg.get("executed"):
                print(f"Received reply for replyId {reply_id}")
                return
        time.sleep(0.1)
    raise AssertionError(f"Reply for replyId {reply_id} not received within {timeout} seconds.")


def wait_for_ws_message(listener, pin, expected_state, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        pin_messages = [msg for msg in listener.get_all_messages() if msg.get("type") == "pinState" and msg.get("pin") == pin]
        if pin_messages and pin_messages[-1].get("state") == expected_state:
            return
        time.sleep(0.1)
    raise AssertionError(f"Expected state {expected_state} for pin {pin} not received within {timeout} seconds.")


def send_serial_message(context, message):
    """Send a message via the serial connection."""
    context.serial_conn.write(f"{message}\n".encode())
    print(f"Sent serial message: {message}")


def wait_for_serial_message(context, expected_response, timeout=30):
    """
    Wait for a specific response from the serial connection.
    """
    start_time = time.time()
    is_regex = isinstance(expected_response, re.Pattern)

    while time.time() - start_time < timeout:
        response = context.serial_conn.readline().decode('ascii', errors='ignore').strip()
        print(f"Received serial response: {response}")
        
        if is_regex:
            if expected_response.match(response):  # Use match() instead of fullmatch()
                print(f"Received expected serial response matching regex: {response}")
                return response
        else:
            if response == expected_response:
                print(f"Received expected serial response: {response}")
                return response

    match_type = "matching regex" if is_regex else "equal to"
    expected_display = expected_response.pattern if is_regex else expected_response
    raise AssertionError(f"Expected serial response '{expected_display}' ({match_type}) not received within {timeout} seconds.")


@given('arduino is in steady state')
def arduino_is_in_steady_state(context):
    wait_for_serial_message(context, re.compile(r"^alp://info/"))


@given('serial message "{message}" is sent')
@when('serial message "{message}" is sent')
def serial_message_is_sent(context, message):
    send_serial_message(context, message)


@when('serial response "{response}" was received')
@then('serial response "{response}" was received')
def serial_response_was_received(context, response):
    wait_for_serial_message(context, response)


@given('the pin {pin} is {mode} monitored')
def step_watch_pin(context, pin, mode):
    reply_id = send_ws_message(context.listener.ws, {"type": "pinMode", "pin": pin, "mode": mode})
    wait_for_reply(context.listener, reply_id)


@given('the pin {pin} is set to {value}')
@when('the pin {pin} is set to {value}')
def step_set_pin(context, pin, value):
    parsed_value = parse_value(value)
    reply_id = send_ws_message(context.listener.ws, {"type": "pinState", "pin": pin, "state": parsed_value})
    wait_for_reply(context.listener, reply_id)


@then('the pin {pin} should be {state}')
def step_check_pin_state(context, pin, state):
    expected_state = parse_value(state)
    wait_for_ws_message(context.listener, pin, expected_state)
