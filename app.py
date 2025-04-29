from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

# 🔹 Definir sectores y horarios
sectores = ["Sector 1", "Sector 2", "Sector 3"]

horarios = []
hora_actual = datetime.strptime("08:00", "%H:%M")
hora_fin = datetime.strptime("17:00", "%H:%M")

while hora_actual <= hora_fin:
    horarios.append(hora_actual.strftime("%H:%M"))
    hora_actual += timedelta(minutes=30)

dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

# 🔹 Boxes por sector
boxes_por_sector = {
    "Sector 1": [6, 8, 10, 12],
    "Sector 2": [7, 8, 9, 10, 11, 13],
    "Sector 3": [6, 7, 9, 11, 12],
}

# 🔹 Profesionales por sector
profesionales_por_sector = {
    "Sector 1": ["Dr. Carlos Molina M.", "Dra Carola Arce", "Dr. Ignacio Valdez", "Dr. Efrén Gutierrez", "Dra. Isabel Chirino",
                 "Dra. Karla Grudski", "Dra. Sofia", "Dra. Giacarla Gambi","Dr. Juan Hernández","Dra. Scarlette Garcia",
                 "Dr. Diego Vallegos","Dr. Andrés Barra","Dr. Joaquín Alvarado","Dr. Omar Pereira","Dr. Oliver Puentes",
                  "Dra. Mirtha Olivares", "Dr. Benjamín Arancibia", "Dr. Leonardo Delgado"],
    "Sector 2": ["Dr. Carlos Molina M.", "Dra Carola Arce", "Dr. Ignacio Valdez", "Dr. Efrén Gutierrez", "Dra. Isabel Chirino",
                 "Dra. Karla Grudski", "Dra. Sofia", "Dra. Giacarla Gambi","Dr. Juan Hernández","Dra. Scarlette Garcia",
                 "Dr. Diego Vallegos","Dr. Andrés Barra","Dr. Joaquín Alvarado","Dr. Omar Pereira","Dr. Oliver Puentes",
                  "Dra. Mirtha Olivares", "Dr. Benjamín Arancibia", "Dr. Leonardo Delgado"],
    "Sector 3": ["Dr. Carlos Molina M.", "Dra Carola Arce", "Dr. Ignacio Valdez", "Dr. Efrén Gutierrez", "Dra. Isabel Chirino",
                 "Dra. Karla Grudski", "Dra. Sofia", "Dra. Giacarla Gambi","Dr. Juan Hernández","Dra. Scarlette Garcia",
                 "Dr. Diego Vallegos","Dr. Andrés Barra","Dr. Joaquín Alvarado","Dr. Omar Pereira","Dr. Oliver Puentes",
                  "Dra. Mirtha Olivares", "Dr. Benjamín Arancibia", "Dr. Leonardo Delgado"],
}

# Archivo donde se guardarán los datos
DATA_FILE = "datos.json"

# Inicializar estado_boxes correctamente si el JSON no existe o está dañado
def cargar_datos():
    """Carga el estado de los boxes desde JSON o lo inicializa si no existe."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                datos = json.load(f)

            # — Convertir claves de box (str → int) para que no se pierdan al merge:
            for sector in datos:
                for dia in datos[sector]:
                    orig = datos[sector][dia]
                    nuevos = {}
                    for box_str, horario_map in orig.items():
                        try:
                            b = int(box_str)
                            nuevos[b] = horario_map
                        except ValueError:
                            pass
                    datos[sector][dia] = nuevos

                # 🔥 Verificar que todas las claves necesarias existen
                for sector in sectores:
                    if sector not in datos:
                        datos[sector] = {}
                    for dia in dias_semana:
                        if dia not in datos[sector]:
                            datos[sector][dia] = {}
                        for box in boxes_por_sector[sector]:
                            if box not in datos[sector][dia]:
                                datos[sector][dia][box] = {horario: "" for horario in horarios}
                            else:
                                for horario in horarios:
                                    if horario not in datos[sector][dia][box]:
                                        datos[sector][dia][box][horario] = ""
                return datos
        except (json.JSONDecodeError, KeyError, TypeError):
            print("⚠️ Error en datos.json, se regenerará automáticamente.")
    
    # Si hay error o no existe, generar nuevo estado_boxes
    return {
        sector: {
            dia: {box: {horario: "" for horario in horarios} for box in boxes_por_sector[sector]}
            for dia in dias_semana
        }
        for sector in sectores
    }

def guardar_datos():
    """Guarda el estado de los boxes en un archivo JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(estado_boxes, f, indent=4)

# Cargar datos al iniciar
estado_boxes = cargar_datos()

@app.route("/", methods=["GET", "POST"])
def index():
    """Página principal que muestra los sectores, horarios y estado de los boxes."""
       
    # Obtener el mes y el año actual
    ahora = datetime.now()
    mes_actual = ahora.strftime("%B")  # Nombre completo del mes
    año_actual = ahora.year

    if request.method == "POST":
        sector = request.form.get("sector")
        dia = request.form.get("dia")
        box = request.form.get("box")  # ❗ No convertir aún a int
        horario_inicio = request.form.get("horario_inicio")
        horario_fin = request.form.get("horario_fin")
        profesional = request.form.get("profesional")

        if not (sector and dia and box and horario_inicio and horario_fin and profesional):
            return "Faltan datos en el formulario"

        try:
            box = int(box)  # ✅ Convertimos aquí con seguridad
        except ValueError:
            return "Error: Box inválido"

        # 🔥 Verificar si el box existe en el sector seleccionado
        if box not in boxes_por_sector.get(sector, []):
            return "Error: Box no pertenece a este sector"

        # 🔥 Asignar el profesional al rango de horarios seleccionado
        horarios_disponibles = [h for h in horarios if horario_inicio <= h <= horario_fin]
        for h in horarios_disponibles:
            estado_boxes[sector][dia][box][h] = profesional

        guardar_datos()  # 🔹 Guarda los cambios en el archivo JSON

        # Redirigir a la página principal con el día seleccionado
        return redirect(f"/?dia={dia}")

        # Obtener el día seleccionado desde la URL
    dia_seleccionado = request.args.get("dia", "Lunes")

    # Calcular la fecha del día seleccionado dentro de esta semana
    semana_inicio = ahora - timedelta(days=ahora.weekday())  # lunes
    idx = dias_semana.index(dia_seleccionado)
    fecha_dia = semana_inicio + timedelta(days=idx)

    # Formatear como "Lunes 28 de abril de 2025"
    mes_formateado = fecha_dia.strftime("%B").capitalize()
    frase_fecha = f"{dia_seleccionado} {fecha_dia.day} de {mes_formateado} de {fecha_dia.year}"

    return render_template(
        "index.html",
        sectores=sectores,
        boxes_por_sector=boxes_por_sector,
        horarios=horarios,
        dias_semana=dias_semana,
        estado_boxes=estado_boxes,
        profesionales_por_sector=profesionales_por_sector,
        dia_seleccionado=dia_seleccionado,
        mes_actual=mes_actual,
        año_actual=año_actual,
        frase_fecha=frase_fecha,  # 👈 nuevo dato para mostrar en index.html
    )


@app.route("/liberar", methods=["POST"])
def liberar_box():
    """Libera un box eliminando la asignación de un profesional en el horario seleccionado y redirige a la página principal."""
    
    sector = request.form.get("sector")
    dia = request.form.get("dia")
    box = request.form.get("box")  # ❗ No convertir aún a int
    horario_inicio = request.form.get("horario_inicio")
    horario_fin = request.form.get("horario_fin")

    if not (sector and dia and box and horario_inicio and horario_fin):
        return "Faltan datos en el formulario"

    try:
        box = int(box)  # ✅ Convertimos aquí con seguridad
    except ValueError:
        return "Error: Box inválido"

    # 🔥 Verificar si el box existe en el sector seleccionado
    if box not in boxes_por_sector.get(sector, []):
        return "Error: Box no pertenece a este sector"

    # 🔥 Liberar el rango de horarios seleccionado
    horarios_disponibles = [h for h in horarios if horario_inicio <= h <= horario_fin]
    for h in horarios_disponibles:
        estado_boxes[sector][dia][box][h] = ""  # Borra la asignación

    guardar_datos()  # 🔹 Guarda los cambios en el archivo JSON

    # Redirigir a la página principal con el día seleccionado
    return redirect(f"/?dia={dia}")

if __name__ == "__main__":
    app.run(host="10.68.118.135", port=3000, debug=True)
