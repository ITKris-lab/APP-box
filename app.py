from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
from supabase_client import supabase
import calendar

app = Flask(__name__)

# 🔹 Definir sectores y horarios
sectores = ["Sector 1", "Sector 2", "Sector 3"]

# 🔹 Boxes por sector
boxes_por_sector = {
    "Sector 1": [6, 8, 10, 12],
    "Sector 2": [7, 8, 9, 10, 11, 13],
    "Sector 3": [6, 7, 9, 11, 12],
}

# 🔹 Profesionales por sector
profesionales_por_sector = {
    sector: [
        "Dr. Carlos Molina M.", "Dra Carola Arce", "Dr. Ignacio Valdez", "Dr. Efrén Gutierrez", "Dra. Isabel Chirino",
        "Dra. Karla Grudski", "Dra. Sofia", "Dra. Giacarla Gambi", "Dr. Juan Hernández", "Dra. Scarlette Garcia",
        "Dr. Diego Vallegos", "Dr. Andrés Barra", "Dr. Joaquín Alvarado", "Dr. Omar Pereira", "Dr. Oliver Puentes",
        "Dra. Mirtha Olivares", "Dr. Benjamín Arancibia", "Dr. Leonardo Delgado", "Dr. Javier Arias", "Dra.Amy Acosta",
        "Ocupado"
    ] for sector in sectores
}

# 🔹 Generar lista de horarios
horarios = []
hora_actual = datetime.strptime("08:00", "%H:%M")
hora_fin = datetime.strptime("17:00", "%H:%M")
while hora_actual <= hora_fin:
    horarios.append(hora_actual.strftime("%H:%M"))
    hora_actual += timedelta(minutes=30)

def obtener_estado_boxes(fecha):
    """Consulta Supabase y devuelve un diccionario estado_boxes estructurado por sector > fecha > box > horario."""
    data = supabase.table("asignaciones").select("*").execute().data
    estado = {
        s: {
            fecha.strftime("%Y-%m-%d"): {
                box: {h: "" for h in horarios}
                for box in boxes_por_sector[s]
            }
            for s in sectores
        }
    }

    for fila in data:
        sector = fila["sector"]
        dia = fila["dia"]
        box = fila["box"]
        horario = fila["horario"]
        profesional = fila["profesional"]

        if sector in estado and dia in estado[sector] and box in estado[sector][dia]:
            estado[sector][dia][box][horario] = profesional

    return estado

def obtener_calendario_mes(fecha):
    """Genera el calendario del mes para la fecha dada."""
    cal = calendar.monthcalendar(fecha.year, fecha.month)
    return cal

@app.route("/", methods=["GET", "POST"])
def index():
    ahora = datetime.now()
    mes_actual = ahora.strftime("%B")
    año_actual = ahora.year

    # Obtener la fecha seleccionada o usar la fecha actual
    fecha_str = request.args.get("fecha")
    if fecha_str:
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            fecha_seleccionada = ahora
    else:
        fecha_seleccionada = ahora

    if request.method == "POST":
        sector = request.form.get("sector")
        fecha = request.form.get("fecha")
        box = request.form.get("box")
        horario_inicio = request.form.get("horario_inicio")
        horario_fin = request.form.get("horario_fin")
        profesional = request.form.get("profesional")

        if not (sector and fecha and box and horario_inicio and horario_fin and profesional):
            return "Faltan datos en el formulario"
        
        try:
            box = int(box)
        except ValueError:
            return "Error: Box inválido"

        if box not in boxes_por_sector.get(sector, []):
            return "Error: Box no pertenece a este sector"

        horarios_disponibles = [h for h in horarios if horario_inicio <= h <= horario_fin]

        # 🔹 Eliminar asignaciones anteriores en ese rango
        for h in horarios_disponibles:
            supabase.table("asignaciones").delete().match({
                "sector": sector,
                "dia": fecha,
                "box": box,
                "horario": h
            }).execute()
            supabase.table("asignaciones").insert({
                "sector": sector,
                "dia": fecha,
                "box": box,
                "horario": h,
                "profesional": profesional
            }).execute()

        return redirect(f"/?fecha={fecha}")

    estado_boxes = obtener_estado_boxes(fecha_seleccionada)
    calendario = obtener_calendario_mes(fecha_seleccionada)
    
    # Formatear la fecha para mostrar
    frase_fecha = fecha_seleccionada.strftime("%A %d de %B de %Y").capitalize()

    return render_template(
        "index.html",
        sectores=sectores,
        boxes_por_sector=boxes_por_sector,
        horarios=horarios,
        estado_boxes=estado_boxes,
        profesionales_por_sector=profesionales_por_sector,
        fecha_seleccionada=fecha_seleccionada.strftime("%Y-%m-%d"),
        mes_actual=mes_actual,
        año_actual=año_actual,
        frase_fecha=frase_fecha,
        calendario=calendario,
    )

@app.route("/liberar", methods=["POST"])
def liberar_box():
    sector = request.form.get("sector")
    fecha = request.form.get("fecha")
    box = request.form.get("box")
    horario_inicio = request.form.get("horario_inicio")
    horario_fin = request.form.get("horario_fin")

    if not (sector and fecha and box and horario_inicio and horario_fin):
        return "Faltan datos en el formulario"

    try:
        box = int(box)
    except ValueError:
        return "Error: Box inválido"

    if box not in boxes_por_sector.get(sector, []):
        return "Error: Box no pertenece a este sector"

    horarios_disponibles = [h for h in horarios if horario_inicio <= h <= horario_fin]

    for h in horarios_disponibles:
        supabase.table("asignaciones").delete().match({
            "sector": sector,
            "dia": fecha,
            "box": box,
            "horario": h
        }).execute()

    return redirect(f"/?fecha={fecha}")

if __name__ == "__main__":
    app.run(host="10.68.118.135", port=3000, debug=True)
