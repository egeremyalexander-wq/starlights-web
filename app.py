import os
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, session
from markupsafe import escape

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-production")

HTML = '''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Starlights Creative Studio</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#071424;color:#eef8fc;font:16px Arial,sans-serif;line-height:1.6}section{max-width:1100px;margin:auto;padding:80px 25px}.top{display:flex;justify-content:space-between;padding:20px 25px;border-bottom:1px solid #22425b}.logo{letter-spacing:2px;font-weight:bold;color:#82e9f3}.top a{color:#b9d6e7;text-decoration:none;margin-left:18px}.hero{min-height:570px;display:grid;place-items:center;text-align:center;background:radial-gradient(circle,#155777 0,#071424 62%)}h1,h2{font-family:Georgia,serif;font-weight:normal;line-height:1.05}h1{font-size:clamp(52px,9vw,100px);margin:0}h2{font-size:clamp(38px,5vw,62px)}em{color:#82e9f3}.hero p,.intro{max-width:560px;color:#b9d6e7;margin:25px auto}.btn{display:inline-block;background:#82e9f3;color:#062039;text-decoration:none;border:0;padding:14px 20px;font-weight:bold;cursor:pointer}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{padding:28px;background:#0d2a44;border:1px solid #27536c}.card h3{font:28px Georgia,serif;color:#fff}.card p{color:#b9d6e7}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:25px}.step b{color:#82e9f3;font-size:22px}.contact{text-align:center;background:#0c2943}.form{max-width:520px;margin:30px auto;display:grid;gap:12px;text-align:left}.form input,.form textarea{width:100%;padding:13px;background:#061827;color:white;border:1px solid #4b91a8}.form textarea{min-height:110px}.notice{color:#9bf3c5;font-weight:bold}@media(max-width:700px){.top nav{display:none}.cards,.steps{grid-template-columns:1fr}section{padding:60px 20px}}
</style></head><body><header class="top"><span class="logo">✦ STARLIGHTS</span><nav><a href="#servicios">Servicios</a><a href="#contacto">Contacto</a></nav></header><section class="hero"><div><p class="logo">CREATIVE STUDIO</p><h1>Hacemos que las<br><em>marcas brillen.</em></h1><p>Producción creativa para artistas, marcas y proyectos que quieren destacar.</p><a class="btn" href="#contacto">Inicia tu proyecto</a></div></section><section id="servicios"><p class="logo">SERVICIOS</p><h2>Creación con <em>dirección.</em></h2><p class="intro">Llevamos tu idea de la inspiración a una experiencia profesional.</p><div class="cards"><div class="card"><b>01</b><h3>Producción musical</h3><p>Sonido, grabación y producción para llevar tus canciones al siguiente nivel.</p></div><div class="card"><b>02</b><h3>Edición de video</h3><p>Videos dinámicos y profesionales para contar tu historia.</p></div><div class="card"><b>03</b><h3>Sesión fotográfica</h3><p>Imágenes con intención para tu marca, proyecto o perfil artístico.</p></div><div class="card"><b>04</b><h3>Talleres y asesorías</h3><p>Acompañamiento práctico para que desarrolles tus ideas con confianza.</p></div></div></section><section><p class="logo">NUESTRO PROCESO</p><h2>De una idea a una <em>gran luz.</em></h2><div class="steps"><div class="step"><b>01</b><h3>Escuchamos</h3><p>Entendemos tu proyecto.</p></div><div class="step"><b>02</b><h3>Creamos</h3><p>Diseñamos una solución con identidad.</p></div><div class="step"><b>03</b><h3>Publicamos</h3><p>La compartimos con el mundo.</p></div></div></section><section id="contacto" class="contact"><p class="logo">¿TIENES UNA IDEA?</p><h2>Hagamos que <em>brille.</em></h2>''' 

HTML_END = '''<form class="form" method="post" action="/contacto"><input name="nombre" placeholder="Tu nombre" required><input name="correo" type="email" placeholder="Tu correo" required><textarea name="mensaje" placeholder="Cuéntanos tu idea" required></textarea><button class="btn">Enviar mensaje</button></form><p class="notice">{notice}</p></section></body></html>'''


def database():
    db = sqlite3.connect("mensajes.db")
    db.execute("CREATE TABLE IF NOT EXISTS mensajes (nombre, correo, mensaje, fecha)")
    return db


@app.route("/")
def inicio():
    return HTML + HTML_END.format(notice="")


@app.route("/contacto", methods=["POST"])
def contacto():
    db = database()
    db.execute("INSERT INTO mensajes VALUES (?, ?, ?, ?)", (request.form["nombre"], request.form["correo"], request.form["mensaje"], str(datetime.now())))
    db.commit()
    db.close()
    return HTML + HTML_END.format(notice="¡Mensaje guardado correctamente!")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        return "Configura ADMIN_PASSWORD en Render antes de abrir esta página.", 503
    if request.method == "POST":
        if request.form.get("password") == password:
            session["admin"] = True
            return redirect("/admin")
        return "Contraseña incorrecta. <a href='/admin'>Intentar otra vez</a>", 401
    if not session.get("admin"):
        return '''<!doctype html><title>Starlights Admin</title><style>body{background:#071424;color:#eef8fc;font:16px Arial;padding:50px}form{max-width:340px;display:grid;gap:12px}input,button{padding:12px}button{background:#82e9f3;border:0;cursor:pointer}</style><h1>Starlights · Mensajes</h1><form method="post"><input type="password" name="password" placeholder="Contraseña" required><button>Entrar</button></form>'''
    db = database()
    rows = db.execute("SELECT nombre, correo, mensaje, fecha FROM mensajes ORDER BY fecha DESC").fetchall()
    db.close()
    table = "".join(f"<tr><td>{escape(r[0])}</td><td>{escape(r[1])}</td><td>{escape(r[2])}</td><td>{escape(r[3])}</td></tr>" for r in rows)
    return f'''<!doctype html><title>Starlights Admin</title><style>body{{background:#071424;color:#eef8fc;font:15px Arial;padding:35px}}table{{width:100%;border-collapse:collapse}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #31546c}}th{{color:#82e9f3}}a{{color:#82e9f3}}</style><h1>Mensajes recibidos</h1><p>Total: {len(rows)}</p><table><tr><th>Nombre</th><th>Correo</th><th>Mensaje</th><th>Fecha</th></tr>{table}</table>'''


if __name__ == "__main__":
    app.run(debug=True)
