from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
from supabase_client import supabase

app = Flask(__name__)

# 🔹 Definir sectores y horarios
sectores = ["Sector 1", "Sector 2", "Sector 3"]
dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

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
        "Dra. Mirtha Olivares", "Dr. Benjamín Arancibia", "Dr. Leonardo Delgado"
    ] for sector in sectores
}

# 🔹 Generar lista de horarios
horarios = []
hora_actual = datetime.strptime("08:00", "%H:%M")
hora_fin = datetime.strptime("17:00", "%H:%M")
while hora_actual <= hora_fin:
    horarios.append(hora_actual.strftime("%H:%M"))
    hora_actual += timedelta(minutes=30)

def obtener_estado_boxes():
    """Consulta Supabase y devuelve un diccionario estado_boxes estructurado por sector > día > box > horario."""
    data = supabase.table("asignaciones").select("*").execute().data
    estado = {
        sector: {
            dia: {
                box: {h: "" for h in horarios}
                for box in boxes_por_sector[sector]
            }
            for dia in dias_semana
        }
        for sector in sectores
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

@app.route("/", methods=["GET", "POST"])
def index():
    ahora = datetime.now()
    mes_actual = ahora.strftime("%B")
    año_actual = ahora.year

    if request.method == "POST":
        sector = request.form.get("sector")
        dia = request.form.get("dia")
        box = request.form.get("box")
        horario_inicio = request.form.get("horario_inicio")
        horario_fin = request.form.get("horario_fin")
        profesional = request.form.get("profesional")

        if not (sector and dia and box and horario_inicio and horario_fin and profesional):
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
                "dia": dia,
                "box": box,
                "horario": h
            }).execute()
            supabase.table("asignaciones").insert({
                "sector": sector,
                "dia": dia,
                "box": box,
                "horario": h,
                "profesional": profesional
            }).execute()

        return redirect(f"/?dia={dia}")

    dia_seleccionado = request.args.get("dia", "Lunes")
    idx = dias_semana.index(dia_seleccionado)
    semana_inicio = ahora - timedelta(days=ahora.weekday())
    fecha_dia = semana_inicio + timedelta(days=idx)
    mes_formateado = fecha_dia.strftime("%B").capitalize()
    frase_fecha = f"{dia_seleccionado} {fecha_dia.day} de {mes_formateado} de {fecha_dia.year}"

    estado_boxes = obtener_estado_boxes()

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
        frase_fecha=frase_fecha,
    )

@app.route("/liberar", methods=["POST"])
def liberar_box():
    sector = request.form.get("sector")
    dia = request.form.get("dia")
    box = request.form.get("box")
    horario_inicio = request.form.get("horario_inicio")
    horario_fin = request.form.get("horario_fin")

    if not (sector and dia and box and horario_inicio and horario_fin):
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
            "dia": dia,
            "box": box,
            "horario": h
        }).execute()

    return redirect(f"/?dia={dia}")

if __name__ == "__main__":
    app.run(host="10.68.118.135", port=3000, debug=True)
