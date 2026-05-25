import os
print("=== Iniciando run.py ===")
from app import create_app
print("=== create_app importado ===")

app = create_app()
print("=== App creada ===")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)