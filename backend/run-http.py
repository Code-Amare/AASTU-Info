import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    python = sys.executable

    uvicorn_cmd = [
        python,
        "-m",
        "uvicorn",
        "core.asgi:application",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
        "--reload-dir",
        BASE_DIR,
        "--lifespan",
        "off",
    ]

    print("Starting Django HTTP server on http://0.0.0.0:8000 ...")

    subprocess.run(
        uvicorn_cmd,
        cwd=BASE_DIR,
    )


if __name__ == "__main__":
    main()
