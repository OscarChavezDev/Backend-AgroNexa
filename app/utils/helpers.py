from bson import ObjectId
from datetime import datetime, timezone


def serialize_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    for key, value in list(doc.items()):
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, list):
            doc[key] = [_serialize_value(v) for v in value]
        elif isinstance(value, dict):
            doc[key] = _serialize_nested(value)
    return doc


def _serialize_nested(d):
    result = {}
    for k, v in d.items():
        result[k] = _serialize_value(v)
    return result


def _serialize_value(v):
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, dict):
        return _serialize_nested(v)
    if isinstance(v, list):
        return [_serialize_value(i) for i in v]
    return v


def now_utc():
    return datetime.now(timezone.utc)
