"""Version HTML del email de confirmacion, con la paleta y la tipografia de EcoHarmony Park.

Los clientes de correo ignoran las hojas de estilo y buena parte del CSS moderno, por eso se usan
tablas y estilos en cada elemento. Las imagenes (logo y QR) se referencian con `cid:` y viajan
dentro del propio mensaje, asi se ven sin que el lector tenga que "cargar imagenes remotas".
Todo dato que escribio el usuario se escapa antes de entrar al HTML.
"""

from html import escape

VERDE_OSCURO = "#386641"
VERDE = "#6A994E"
LIMA = "#A7C957"
CREMA = "#F2E8CF"
ROJO = "#BC4749"
FUENTE = "Lato, 'Segoe UI', Arial, sans-serif"


def armar_html(inscripcion, cantidad_de_qrs):
    horario = inscripcion.horario
    detalle = [
        ("Actividad", inscripcion.actividad.nombre),
        ("Código de reserva", inscripcion.codigo),
        ("Fecha", f"{horario.fecha:%d/%m/%Y}"),
        ("Horario", f"{horario.hora_inicio:%H:%M} a {horario.hora_fin:%H:%M}"),
        ("Personas", f"{len(inscripcion.visitantes)} personas"),
    ]
    visitantes = "".join(
        _visitante(numero, visitante.nombre, con_qr=numero <= cantidad_de_qrs)
        for numero, visitante in enumerate(inscripcion.visitantes, start=1)
    )
    return f"""<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Inscripción confirmada</title></head>
<body style="margin:0;padding:0;background:{CREMA};font-family: {FUENTE};color:{VERDE_OSCURO};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CREMA};">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0"
  style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;
  border:1px solid {LIMA};">
<tr><td align="center" style="background:#F8F9F3;padding:20px 16px 12px;">
<img src="cid:logo" alt="EcoHarmony Park" width="200" style="display:block;border:0;height:auto;">
</td></tr>
<tr><td align="center" style="background:{VERDE_OSCURO};padding:18px 16px;">
<h1 style="margin:0;font-family: {FUENTE};font-size:22px;color:{CREMA};">
¡Tu inscripción está confirmada!</h1>
</td></tr>
<tr><td style="padding:22px 28px 8px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
  style="font-family: {FUENTE};font-size:15px;">
{"".join(_fila(nombre, valor) for nombre, valor in detalle)}
</table>
</td></tr>
<tr><td style="padding:8px 28px 4px;">
<h2 style="margin:12px 0 4px;font-family: {FUENTE};font-size:17px;color:{VERDE};">
Visitantes y códigos QR</h2>
</td></tr>
<tr><td style="padding:0 28px 8px;">{visitantes}</td></tr>
<tr><td style="padding:8px 28px 22px;">
<p style="margin:0;padding:12px 14px;background:{CREMA};border-left:4px solid {ROJO};
  font-family: {FUENTE};font-size:14px;">
El día de la actividad presentá tu <strong>DNI</strong> y el código <strong>QR</strong> de cada
visitante. También los encontrás adjuntos a este mensaje.</p>
</td></tr>
<tr><td align="center" style="background:{VERDE};padding:14px 16px;">
<p style="margin:0;font-family: {FUENTE};font-size:13px;color:#ffffff;">
EcoHarmony Park · Inscripción a actividades</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>
"""


def _fila(nombre, valor):
    return (
        f'<tr><td style="padding:6px 0;border-bottom:1px solid {CREMA};color:{VERDE};'
        f'font-weight:bold;width:40%;">{escape(nombre)}</td>'
        f'<td style="padding:6px 0;border-bottom:1px solid {CREMA};">{escape(str(valor))}</td></tr>'
    )


def _visitante(numero, nombre, con_qr):
    qr = (
        f'<img src="cid:qr-visitante-{numero}" alt="Código QR de {escape(nombre)}" width="150" '
        'style="display:block;border:0;height:auto;">'
        if con_qr
        else ""
    )
    return (
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        f'style="margin:8px 0;border:1px solid {LIMA};border-radius:10px;">'
        f'<tr><td style="padding:12px 14px;font-family: {FUENTE};font-size:15px;">'
        f"<strong>Visitante {numero}</strong><br>{escape(nombre)}</td>"
        f'<td align="right" style="padding:10px 14px;">{qr}</td></tr></table>'
    )
