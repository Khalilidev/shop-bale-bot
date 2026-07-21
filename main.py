"""
Run bot and webapp together.
"""

import os
import sys
import time
import subprocess
import threading
from utils.free_port import free_port

BOT_SCRIPT = "run_bot.py"
WEBAPP_APP = "webapp.main:app"
PORT = 8000

DASH_LINE = "*" * 50


def run_bot():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    subprocess.run(
        [sys.executable, BOT_SCRIPT],
        env=env
    )


def run_webapp():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    subprocess.run(
        [
            "uvicorn",
            WEBAPP_APP,
            "--host", "0.0.0.0",
            "--port", str(PORT),
            "--reload"
        ],
        env=env
    )


def main():
    free_port()
    print(DASH_LINE)
    print("Starting Services")
    print(DASH_LINE)

    print(f"Bot Script : {BOT_SCRIPT}")
    print(f"Web App    : http://localhost:{PORT}")
    print(f"Test URL   : http://localhost:{PORT}/?startapp=test")

    print(DASH_LINE)
    print("Press Ctrl+C to stop all services.")
    print(DASH_LINE)

    bot = threading.Thread(target=run_bot, daemon=True)
    web = threading.Thread(target=run_webapp, daemon=True)

    bot.start()
    web.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print(DASH_LINE)
        print("Stopping Services...")
        print(DASH_LINE)


if __name__ == "__main__":
    main()