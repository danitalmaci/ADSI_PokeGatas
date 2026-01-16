document.addEventListener('DOMContentLoaded', function() {

    const menuToggle = document.getElementById('menuToggle');
    const menuClose = document.getElementById('menuClose');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    // Función para alternar el estado
    function toggleMenu() {
        sidebar.classList.toggle('active');      // Muestra el menú
        mainContent.classList.toggle('shifted'); // Empuja el contenido
        menuToggle.classList.toggle('shifted');  // Mueve el botón de hamburguesa
    }

    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMenu);
    }
    
    if (menuClose) {
        menuClose.addEventListener('click', toggleMenu);
    }

});