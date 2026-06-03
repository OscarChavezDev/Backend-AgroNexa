from app.utils.helpers import serialize_doc
from . import repository as repo


def enviar_feedback(user_id, nombre, apellido, correo, mensaje):
    if not mensaje or not mensaje.strip():
        return None, "El mensaje no puede estar vacío"
    doc = {
        "userId":   user_id,
        "nombre":   nombre,
        "apellido": apellido,
        "correo":   correo,
        "tipo":     "feedback",
        "mensaje":  mensaje.strip(),
    }
    msg_id = repo.crear(doc)
    return {"id": msg_id}, None


def crear_notif_reingreso(user_id, nombre, apellido, correo):
    doc = {
        "userId":   user_id,
        "nombre":   nombre,
        "apellido": apellido,
        "correo":   correo,
        "tipo":     "reingreso",
        "mensaje":  f"{nombre} {apellido} volvió a iniciar sesión tras un período de inactividad.",
    }
    repo.crear(doc)


def listar_mensajes():
    return [serialize_doc(m) for m in repo.listar_todos()], None


def conteo():
    return {"noLeidos": repo.conteo_no_leidos()}, None


def marcar_leido(mensaje_id):
    repo.marcar_leido(mensaje_id)
    return {"ok": True}, None


def marcar_todos_leidos():
    repo.marcar_todos_leidos()
    return {"ok": True}, None
