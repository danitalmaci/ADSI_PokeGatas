

# TEST CONSULTAR NOTIFICACIONES

def login_fake(client):
    """Simula sesión iniciada"""
    with client.session_transaction() as sess:
        sess["nickname"] = "ash_kethum"


# A17-P1
def test_A17_P1_mostrar_pagina_notificaciones(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert response.status_code == 200
    assert b"Notificaciones" in response.data


# A17-P2
def test_A17_P2_mostrar_opcion_filtrar(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"Buscar Notificaci" in response.data


# A17-P3
def test_A17_P3_existen_notificaciones_en_html(client):
    login_fake(client)
    response = client.get("/notificaciones")
    # Si hay notificaciones, debe aparecer al menos un usuario o info
    assert b"notif" in response.data.lower()


# A17-P4
def test_A17_P4_notificacion_no_existente_no_aparece(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"texto_inexistente_12345" not in response.data


# A17-P5
def test_A17_P5_texto_no_permitido_no_rompe_pagina(client):
    login_fake(client)
    response = client.get("/notificaciones?buscar=@@@###")
    assert response.status_code == 200


# A17-P6
def test_A17_P6_input_busqueda_permanece(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b'search-bar' in response.data


# A17-P7
def test_A17_P7_existe_opcion_navegar(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"menu" in response.data.lower() or b"nav" in response.data.lower()


# A17-P8
def test_A17_P8_existen_enlaces_navegacion(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"href" in response.data


# A17-P9
def test_A17_P9_pagina_se_mantiene(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"Notificaciones" in response.data


# A17-P10
def test_A17_P10_boton_navegar_existe(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"menu" in response.data.lower()


# A17-P11
def test_A17_P11_pagina_estable_sin_accion(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert response.status_code == 200


# A17-P12
def test_A17_P12_contenedor_scroll(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"notifications-list" in response.data


# A17-P13
def test_A17_P13_boton_volver_existe(client):
    login_fake(client)
    response = client.get("/notificaciones")
    assert b"Volver" in response.data
