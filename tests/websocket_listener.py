import websocket
import threading
import queue
import json

class WebSocketListener:
    def __init__(self, ws):
        """
        Initialize the WebSocketListener with the WebSocket connection.
        :param ws: WebSocket object
        """
        self.ws = ws
        self.queue = queue.Queue()
        self.running = True

    def start(self):
        """
        Start a background thread that listens for WebSocket messages.
        """
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def _listen(self):
        """
        Continuously listen for WebSocket messages and add them to the queue.
        """
        while self.running:
            try:
                message = self.ws.recv()
                if not message:
                    # Skip empty messages
                    continue
                try:
                    parsed_message = json.loads(message)
                    print(f"Background listener received: {parsed_message}")
                    self.queue.put(parsed_message)
                except json.JSONDecodeError as e:
                    print(f"Received invalid JSON message: {message}, error: {e}")
                    
            except websocket.WebSocketTimeoutException:
                print("WebSocket recv timed out.")
            except websocket.WebSocketConnectionClosedException:
                print("WebSocket connection closed.")
                self.running = False
            except Exception as e:
                print(f"Error in WebSocket listener: {e}")
                self.running = False

    def stop(self):
        """
        Stop the WebSocket listener and close the WebSocket connection.
        """
        if not self.running:
            return  # Already stopped

        self.running = False  # Signal the listener to stop
        try:
            if self.ws:
                self.ws.close()  # Close the WebSocket connection
                print("WebSocket connection closed.")
        except Exception as e:
            print(f"Error closing WebSocket connection: {e}")

        if self.thread:
            self.thread.join()  # Wait for the listener thread to finish
            print("WebSocket listener thread stopped.")

    def get_message(self, timeout=None):
        """
        Get the next message from the queue.
        :param timeout: Maximum time to wait for a message (in seconds)
        :return: The next message or None if the timeout expires
        """
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_all_messages(self):
        """
        Get all messages from the queue without removing them.
        :return: A list of all messages in the queue
        """
        return list(self.queue.queue)  # Return a copy of the current messages in the queue

