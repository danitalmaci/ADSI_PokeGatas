#PRUEBAS CONSULTAR POKEDEX

def test_pokedex_interaccion(driver):
    # 1️⃣ Abrir la Pokédex
    driver.get(f"{BASE_URL}/pokedex")

    # A19-P1: seleccionar un Pokémon
    first_pokemon = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".pokemon-card a"))
    )
    pokemon_name = first_pokemon.text
    first_pokemon.click()
    
    # Verificar que se abrió la página de ese Pokémon
    header_name = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".pokemon-name"))
    )
    assert pokemon_name in header_name.text

    # A19-P2: mover barra vertical (scroll)
    container = driver.find_element(By.CSS_SELECTOR, ".pokedex-grid")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
    scroll_pos = driver.execute_script("return arguments[0].scrollTop", container)
    assert scroll_pos > 0

    # A19-P3: seleccionar opción de "Filtrar" (click en input de nombre)
    filtro_input = driver.find_element(By.CSS_SELECTOR, ".filter-input[name='nombre']")
    filtro_input.click()
    assert filtro_input.is_displayed()

    # A19-P4: seleccionar opción "Navegar" (tres rayas)
    menu_btn = driver.find_element(By.CSS_SELECTOR, ".menu-btn")  # Ajustar selector según tu HTML
    menu_btn.click()
    nav_options = driver.find_elements(By.CSS_SELECTOR, ".nav-option")
    assert len(nav_options) > 0

    # A19-P5: seleccionar una opción de navegación
    nav_options[0].click()
    # Verificar que se cambió la página
    assert driver.current_url != f"{BASE_URL}/pokedex"

    # A19-P6: abrir menú y no seleccionar nada
    driver.get(f"{BASE_URL}/pokedex")
    menu_btn = driver.find_element(By.CSS_SELECTOR, ".menu-btn")
    menu_btn.click()
    # Sin selección, la página sigue en Pokédex
    assert driver.current_url == f"{BASE_URL}/pokedex"

    # A19-P7: abrir y cerrar menú
    menu_btn.click()  # abre
    menu_btn.click()  # cierra
    # Verificamos que el menú desapareció (opcional)
    nav_options = driver.find_elements(By.CSS_SELECTOR, ".nav-option")
    assert len(nav_options) == 0

    # A19-P8: seleccionar icono ChatBot
    chatbot_icon = driver.find_element(By.CSS_SELECTOR, ".chatbot-btn")  # Ajusta selector
    chatbot_icon.click()
    # Verificamos que se abrió la página del ChatBot
    assert "chatbot" in driver.current_url

#PRUEBAS VER INFORMACIÓN POKEMON

def test_info_pokemon(driver):
    # Abrir la página de notificaciones
    driver.get(f"{BASE_URL}/notificaciones")

    # A20-P1: seleccionar opción "Navegar" (tres rayas)
    menu_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".menu-btn"))  # Ajustar selector según tu HTML
    )
    menu_btn.click()

    nav_options = driver.find_elements(By.CSS_SELECTOR, ".nav-option")
    assert len(nav_options) > 0  # Opciones de navegación se muestran

    # A20-P2: seleccionar una opción de navegación
    first_option = nav_options[0]
    first_option.click()
    # Verificar que la página cambió
    assert driver.current_url != f"{BASE_URL}/notificaciones"

    # Volver a la página de notificaciones para siguientes pruebas
    driver.get(f"{BASE_URL}/notificaciones")

    # A20-P3: abrir menú y no seleccionar nada
    menu_btn = driver.find_element(By.CSS_SELECTOR, ".menu-btn")
    menu_btn.click()
    # Sin selección, la página sigue igual
    assert driver.current_url == f"{BASE_URL}/notificaciones"

    # A20-P4: abrir y cerrar menú
    menu_btn.click()  # cierra menú
    nav_options = driver.find_elements(By.CSS_SELECTOR, ".nav-option")
    assert len(nav_options) == 0  # Opciones de navegación ya no visibles

    # A20-P5: seleccionar opción "Volver" (flecha abajo izquierda)
    volver_btn = driver.find_element(By.CSS_SELECTOR, ".btn-back-home")  # Ajustar selector según tu HTML
    volver_btn.click()
    # Verificar que volvió a la página principal
    assert driver.current_url == f"{BASE_URL}/"