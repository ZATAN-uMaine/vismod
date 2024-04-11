document.addEventListener('DOMContentLoaded', (event) => {
    // Enable when the system color scheme is dark.
    DarkReader.enable({
        brightness: 100,
        contrast: 100,
        sepia: 0
    });

    // Stop watching for the system color scheme.
    DarkReader.auto(false);
});
