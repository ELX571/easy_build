import threading
import time
import requests
import logging

logger = logging.getLogger(__name__)

def ping_server(url):
    while True:
        try:
            time.sleep(600)  # 10 minutes
            response = requests.get(url)
            logger.info(f"Keep-alive ping sent to {url}, status: {response.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")

def start_keep_alive(url):
    thread = threading.Thread(target=ping_server, args=(url,))
    thread.daemon = True
    thread.start()
