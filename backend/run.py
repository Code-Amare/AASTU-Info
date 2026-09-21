import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CERT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "certs", "cert.pem"))

KEY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "certs", "key.pem"))


def main():
    if not (os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH)):
        print("Missing certs. Run this once from the certs/ folder:")
        print("  mkcert -install")
        print('  mkcert localhost "*.localhost" 127.0.0.1 ::1')
        print("Then rename the output files to cert.pem / key.pem")
        sys.exit(1)

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
        "--ssl-certfile",
        CERT_PATH,
        "--ssl-keyfile",
        KEY_PATH,
        "--reload",
        "--reload-dir",
        BASE_DIR,
        "--lifespan",
        "off",
    ]

    print("Starting Django HTTPS server...")
    print("Certificate:", CERT_PATH)
    print("Key:", KEY_PATH)

    subprocess.run(
        uvicorn_cmd,
        cwd=BASE_DIR,
    )


if __name__ == "__main__":
    main()
