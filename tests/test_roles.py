from app.modules.auth.models import build_role_filter, build_user, normalize_role


def test_institucional_role_is_normalized_to_institucion():
    assert normalize_role("institucional") == "institucion"


def test_build_role_filter_includes_legacy_institucional_alias():
    assert build_role_filter("institucion") == {"$in": ["institucion", "institucional"]}
    assert build_role_filter("institucional") == {"$in": ["institucion", "institucional"]}


def test_build_user_stores_canonical_institucion_role():
    user = build_user(
        nombre="Universidad",
        apellido="Demo",
        correo="udh@udh.edu.pe",
        password_hash="hash",
        rol="institucional",
    )

    assert user["rol"] == "institucion"
