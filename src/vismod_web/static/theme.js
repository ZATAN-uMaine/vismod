document.addEventListener('DOMContentLoaded', (event) => {
    DarkReader.setFetchMethod(window.fetch);

    const plots = Array.from(document.getElementsByClassName("plot-frame"));
    plots.forEach((plotFrame) => {
        plotFrame.contentWindow.postMessage('toggleTheme', '*');
    });

    window.addEventListener("message", (event) => {
        if (event.data === "PlotlyAppendLoaded") {
            if (DarkReader.isEnabled()) {
                event.source.postMessage('toggleTheme', '*');
            }
        }
    });
});