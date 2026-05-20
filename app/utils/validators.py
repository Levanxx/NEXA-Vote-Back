import re
from datetime import datetime

def validate_identity(data):

    required_fields = ["dni", "full_name", "birth_date", "email"]

    for field in required_fields:
        if not data.get(field):
            return f"{field} es requerido"

    # -DNI
    if not data["dni"].isdigit() or len(data["dni"]) != 8:
        return "DNI inválido"

    # Nombres
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{3,100}$", data["full_name"]):
        return "Nombre inválido"

    # Quitar espacios vacíos
    if not data["full_name"].strip():
        return "Nombre inválido"

    # Email
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, data["email"]):
        return "Email inválido"

    # Fecha
    try:
        birth_date = datetime.strptime(data["birth_date"], "%Y-%m-%d")
    except ValueError:
        return "Fecha de nacimiento inválida"

    today = datetime.today()

    # Fecha futura
    if birth_date > today:
        return "Fecha de nacimiento no puede ser futura"

    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    if age < 18:
        return "Debes ser mayor de 18 años"

    if age > 100:
        return "Edad inválida"

    return None