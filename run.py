import os
print("=== 1. Iniciando run.py ===", flush=True)
from app import create_app
print("=== 2. create_app importado ===", flush=True)

app = create_app()
print("=== 3. App creada ===", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)