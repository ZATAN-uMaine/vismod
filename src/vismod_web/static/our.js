/**
 * This callback type is called `modalCallback` and is displayed as a global symbol.
 * @callback modalCallback
 */

/**
 * Convert a JS Date into the format for an HTML input
 * @param {Date} date 
 * @returns date representation (`String`)
 */
function formatDate(date) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${year}-${month}-${day}`
}

/**
 * Converts the time part of a JS date into the format for
 * an <input type="time" />
 * @param {Date} date
 * @returns time representation (`String`)
 */
function formatTime(date) {
    const hours = ('0' + date.getHours()).slice(-2);
    const minutes = ('0' + date.getMinutes()).slice(-2);
    return `${hours}:${minutes}`;
}

/**
 * @param {String} date 
 * @param {String} time 
 * @returns `String` in form YYYY-MM-DDTHH:mm
 */
function formatDateString(date, time) {
    return `${date}T${time}:00`;
}

/**
 * Used to generate filenames for export.
 * @param {Date} date 
 * @returns string YYYY-MM-DD
 */
function prettyPrintDate(date) {
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDay()}`;
}


/**
 * Handle the state of the sensor and time range select controls.
 */
class SensorSelection {
    curSensors = [];
    // one week ago
    startTime = new Date((new Date()).getTime() - 7 * 24 * 60 * 60 * 1000);
    // right now
    endTime = new Date();

    get selectedSensors() {
        return this.curSensors;
    }

    get selectedRange() {
        return { "start": this.startTime, "end": this.endTime };
    }

    constructor() {
        this.createEventHandlers = this.createEventHandlers.bind(this);
        this.updateSelectedDate = this.updateSelectedDate.bind(this);
        document.addEventListener("DOMContentLoaded", this.createEventHandlers);
    }

    /**
     * Run after DomContentLoaded.
     */
    createEventHandlers() {
        // date picker
        const startDaySelector = document.getElementById('startDate');
        const endDaySelector = document.getElementById('endDate');
        const startHourSelector = document.getElementById('startHour');
        const endHourSelector = document.getElementById('endHour');

        startDaySelector.addEventListener("change", this.updateSelectedDate);
        endDaySelector.addEventListener("change", this.updateSelectedDate);
        startHourSelector.addEventListener("change", this.updateSelectedDate);
        endHourSelector.addEventListener("change", this.updateSelectedDate);

        startDaySelector.value = formatDate(this.startTime);
        endDaySelector.value = formatDate(this.endTime);
        startHourSelector.value = "00:00";
        endHourSelector.value = formatTime(this.endTime);
        endDaySelector.max = endDaySelector.value;
        startDaySelector.max = endDaySelector.max;

        // sensor points on diagram
        const circles = document.querySelectorAll('.sensor');
        circles.forEach((circle) => {
            circle.addEventListener('click', () => this.updateSelectedSensors([circle.id]));
        });
        this.updateSelectedSensors([]);
    }

    /**
     * updates all dates in the date range from their `<input>`s
     */
    updateSelectedDate() {
        const startDaySelector = document.getElementById('startDate');
        const startHourSelector = document.getElementById('startHour');
        const startDateString = formatDateString(startDaySelector.value, startHourSelector.value);
        this.startTime = new Date(startDateString);
        const endDaySelector = document.getElementById('endDate');
        const endHourSelector = document.getElementById('endHour');
        const endDateString = formatDateString(endDaySelector.value, endHourSelector.value);
        this.endTime = new Date(endDateString);
        startDaySelector.max = endDaySelector.value;
    }

    /**
     * Updates which sensors are selected for plotting.
     * 
     * @param {String[]} sensor 
     */
    updateSelectedSensors(sensors) {
        this.curSensors = sensors;
        const plotButton = document.getElementById("plot-data-button");
        const downloadButton = document.getElementById("download-data-button");
        plotButton.disabled = (this.curSensors.length === 0);
        downloadButton.disabled = (this.curSensors.length === 0);

        const sensorInfoPanel = document.getElementById("cur-sensor-info-panel");
        if (this.curSensors.length == 0) {
            sensorInfoPanel.innerHTML = "";
        } else {
            sensorInfoPanel.innerHTML = `Current sensors: ${this.curSensors}`;
        }
    }
}

window.sensorSelectSingleton = new SensorSelection();


/**
 * Allows display of a pop-up with arbitrary messages
 */
class Modal {
    modalHolder = null;
    onConfirm = null;
    onCancel = () => { };

    constructor() {
        this.createEventHandlers = this.createEventHandlers.bind(this);
        this.showModal = this.showModal.bind(this);
        document.addEventListener("DOMContentLoaded", this.createEventHandlers);
    }

    createEventHandlers() {
        this.modalHolder = document.getElementById("modal");
        this.modalHolder.classList.add("visually-hidden");

        const confirmer = document.getElementById("modal-confirm-button");
        const canceller = document.getElementById("modal-cancel-button");

        confirmer.addEventListener("click", () => {
            this.modalHolder.classList.add("visually-hidden");
            if (this.onConfirm) {
                this.onConfirm();
            }
        });
        canceller.addEventListener("click", () => {
            this.modalHolder.classList.add("visually-hidden");
            this.onCancel();
        });
    }

    /**
     * Shows the modal.
     * @param {string} message 
     * @param {modalCallback} onCancel 
     * @param {modalCallback=} onConfirm 
     * @returns 
     */
    showModal(message, onCancel, onConfirm) {
        if (!onCancel) {
            return;
        }
        if (!onConfirm) {
            this.onConfirm = null;
            document.getElementById("modal-confirm-button").classList.add("visually-hidden");
        } else {
            document.getElementById("modal-confirm-button").classList.remove("visually-hidden");
        }
        document.getElementById("modal-content").innerHTML = message;
        this.modalHolder.classList.remove("visually-hidden");
    }
}

window.modalSingleton = new Modal();

// misc event handlers
document.addEventListener('DOMContentLoaded', (event) => {
    // theme
    const themeToggles = document.querySelectorAll('.theme-toggle')
    document.body.classList.toggle("dark");
    themeToggles.forEach((toggle) => {
        toggle.addEventListener('click', () => themeSwitch())
    })
    // themeToggle.onclick = function () {
    //     document.body.classList.toggle("dark")
    // }

    //download indiv button
    const downloadButton = document.getElementById("download-data-button");
    downloadButton.addEventListener("click", () => {
        const { start, end } = window.sensorSelectSingleton.selectedRange;
        const sensors = window.sensorSelectSingleton.selectedSensors;
        // if there are no selected sensors, don't send invalid request
        if (sensors.length === 0) {
            return;
        }
        // if the start date is after the end date, don't send invalid request
        if (start.getTime() > end.getTime()) {
            return;
        }
        fetchCSV(sensors, start, end)
            .then((blob) => {
                forceBlobDownload(
                    blob,
                    `pnb-export-${sensors[0]}-${prettyPrintDate(start)}-to-${prettyPrintDate(end)}.csv`
                );
            }).catch((err) => {
                const errString = `An Error Ocurred: <br /> <br /> ${err}`;
                window.modalSingleton.showModal(errString, () => { });
            });
    });

    //download all button
    const downloadAllButton = document.getElementById("downloadAllButton");
    downloadAllButton.addEventListener("click", () => {
        const { start, end } = window.sensorSelectSingleton.selectedRange;
        const sensors = ["all"];
        // if the start date is after the end date, don't send invalid request
        if (start.getTime() > end.getTime()) {
            return;
        }
        fetchCSV(sensors, start, end)
            .then((blob) => {
                forceBlobDownload(
                    blob,
                    `pnb-export-all-${prettyPrintDate(start)}-to-${prettyPrintDate(end)}.csv`
                );
            }).catch((err) => {
                const errString = `An Error Ocurred: <br /> <br /> ${err}`;
                window.modalSingleton.showModal(errString, () => { });
            });
    })

    //plot button
    const plotButton = document.getElementById("plot-data-button");
    plotButton.addEventListener("click", () => {
        const { start, end } = window.sensorSelectSingleton.selectedRange;
        const sensors = window.sensorSelectSingleton.selectedSensors;
        // if there are no selected sensors, don't send invalid request
        if (sensors.length === 0) {
            return;
        }
        // if the start date is after the end date, don't send invalid request
        if (start.getTime() > end.getTime()) {
            return;
        }
        fetchPlot(sensors, start, end)
            .catch((err) => {
                const errString = `An Error Ocurred: <br /> <br /> ${err}`;
                window.modalSingleton.showModal(errString, () => { });
            });
    });

});

/**
 * 
 * @param sensors list of sensor names
 * @param {Date} start 
 * @param {Date} end 
 * @returns `Blob` of csv for download
 */
async function fetchCSV(sensors, start, end) {
    const body = new FormData();
    body.append("start", start.toISOString());
    body.append("end", end.toISOString());
    // TODO: support a lost of sensors
    body.append("sensor", sensors[0]);
    const req = await fetch("/download_csv", {
        method: "POST",
        mode: "same-origin",
        body,
    });
    if (req.status == 200) {
        return req.blob();
    } else if (req.status == 204) {
        throw new Error("No data found for selected date range.");
    }
    else {
        throw new Error(req.text);
    }
}

/**
 * Fetches the HTML for a plotly plot
 * and then places it in the DOM.
 * @param sensors list of sensor names
 * @param {Date} start 
 * @param {Date} end 
 */
async function fetchPlot(sensors, start, end) {
    // show loading indicator
    const loadInd = document.getElementById("plot-bay-loading");
    loadInd.classList.remove("visually-hidden");
    let plotIFrame = document.getElementById("plot-frame");
    if (!plotIFrame) {
        plotIFrame = document.createElement('iframe');
        plotIFrame.setAttribute("id", "plot-frame");
        document.getElementById('plotBay').appendChild(plotIFrame);
        plotIFrame.setAttribute('scrolling', 'no');
        plotIFrame.setAttribute('style', 'border:none;');
        plotIFrame.setAttribute('seamless', 'seamless');
        plotIFrame.setAttribute('height', '525');
        plotIFrame.setAttribute('width', '100%');
    }
    plotIFrame.contentWindow.document.open();
    plotIFrame.contentWindow.document.write("");
    plotIFrame.contentWindow.document.close();

    const location = new URL("/display_plot", window.location.origin);
    location.searchParams.append("start", start.toISOString());
    location.searchParams.append("end", end.toISOString());
    location.searchParams.append("sensor", sensors[0]);
    const req = await fetch(location);
    if (req.status != 200) {
        loadInd.classList.add("visually-hidden");
        throw new Error(req.text);
    }
    const plotHTML = await req.text();

    plotIFrame.contentWindow.document.open();
    plotIFrame.contentWindow.document.write(plotHTML);
    plotIFrame.contentWindow.document.close();

    // supposed to force dark theme on plot when dark theme is on
    // only works if plot has been created first
    if(body.classList.contains('dark')){
        plotIFrame.contentWindow.postMessage('toggleTheme', '*')
    }
    loadInd.classList.add("visually-hidden");
}

/**
 * forces the user's browser to download the content of a Blob
 * @param {Blob} blob 
 * @param {string} filename
 */
function forceBlobDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}


function themeSwitch() {
    document.body.classList.toggle("dark")
    const plotFrame = document.getElementById('plot-frame');
    if(plotFrame){
        plotFrame.contentWindow.postMessage('toggleTheme', '*');
    }
}