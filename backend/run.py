import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "certs", "cert.pem"))
KEY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "certs", "key.pem"))

IS_WINDOWS = os.name == "nt"
NEW_PROCESS_GROUP = subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0


def main():
    if not (os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH)):
        print("Missing certs. Run this once from the certs/ folder:")
        print("  mkcert -install")
        print('  mkcert localhost "*.localhost" 127.0.0.1 ::1')
        print("Then rename the output files to cert.pem / key.pem")
        sys.exit(1)

    python = sys.executable

    celery_worker_cmd = [
        python,
        "-m",
        "celery",
        "-A",
        "core",
        "worker",
        "-l",
        "info",
        "--pool=solo",
    ]
    celery_beat_cmd = [
        python,
        "-m",
        "celery",
        "-A",
        "core",
        "beat",
        "-l",
        "info",
        "--scheduler",
        "django_celery_beat.schedulers:DatabaseScheduler",
    ]

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

    worker = subprocess.Popen(
        celery_worker_cmd, cwd=BASE_DIR, creationflags=NEW_PROCESS_GROUP
    )
    beat = subprocess.Popen(
        celery_beat_cmd, cwd=BASE_DIR, creationflags=NEW_PROCESS_GROUP
    )

    try:
        subprocess.run(uvicorn_cmd, cwd=BASE_DIR)
    finally:
        for p in (worker, beat):
            p.terminate()
        for p in (worker, beat):
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    main()
