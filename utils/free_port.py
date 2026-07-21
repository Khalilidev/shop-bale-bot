import os
import platform
import subprocess
PORT = 8000
def free_port():
    # Do not run on the server.
    if os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT"):
        return
    system = platform.system()
    try:
        if system == "Linux":
            subprocess.run(["fuser", "-k", f"{PORT}/tcp"], check=False)

        elif system == "Windows":
            subprocess.run(
                ["cmd", "/c", f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{PORT}\') do taskkill /F /PID %a'],
                check=False)

    except Exception:
        pass