from flask import jsonify


def success_response(message, data=None, status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def error_response(message, error=None, status=400):
    body = {"success": False, "message": message}
    if error is not None:
        body["error"] = error
    return jsonify(body), status
