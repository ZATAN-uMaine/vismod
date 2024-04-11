document.addEventListener('DOMContentLoaded', (event) => {
    const darkModeEnabled = localStorage.getItem('darkModeEnabled') === 'true';

    if (darkModeEnabled) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }

    document.getElementById('theme-toggle').addEventListener('click', toggleDarkMode);
});

function toggleDarkMode() {
    if (DarkReader.isEnabled()) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

function enableDarkMode() {
    DarkReader.enable({
        brightness: 100,
        contrast: 100,
        sepia: 0
    });
    localStorage.setItem('darkModeEnabled', 'true');
}

function disableDarkMode() {
    DarkReader.disable();
    localStorage.setItem('darkModeEnabled', 'false');
}