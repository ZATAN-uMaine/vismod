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
 * Converts a Date into an ISO 8601 with correct timezone offset.
 * See https://www.reddit.com/r/javascript/comments/3uaemf/how_to_really_get_a_utc_date_object/
 * @param {Date} date
 * @returns string
 */
function dateToIso(date) {
    return date.toISOString()
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
        if (!startDaySelector || !endDaySelector || !startHourSelector || !endHourSelector) {
            return;
        }

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
        this.updateSelectedDate();

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


/**
 *
 * @param sensors list of sensor names
 * @param {Date} start
 * @param {Date} end
 * @returns `Blob` of csv for download
 */
async function fetchCSV(sensors, start, end) {
    const body = new FormData();
    body.append("start", dateToIso(start));
    body.append("end", dateToIso(end));
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
        throw new Error(await req.text());
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

    const location = new URL("/display_plot", window.location.origin);
    location.searchParams.append("start", dateToIso(start));
    location.searchParams.append("end", dateToIso(end));
    location.searchParams.append("sensor", sensors[0]);
    const req = await fetch(location);
    let plotHTML = null;
    try{
        plotHTML = await req.text();
    }
    catch{
        if (req.status == 500) {
            throw new Error("Date Range selected contains corrupted or missing data");
        }
        if (req.status != 200) {
            loadInd.classList.add("visually-hidden");
            throw new Error(await req.text());
        }
    }


    // create new iframe for play
    const plotIFrame = document.createElement('iframe');
    plotIFrame.classList.add("plot-frame");

    // create close button to remove iframe
    const closer = document.createElement("div");
    const closerMain = document.createElement("button");
    closerMain.innerText = "X";
    closer.appendChild(closerMain);
    closer.classList.add("plot-remove-button");
    closerMain.addEventListener("click", () => {
        plotIFrame.remove();
        closer.remove();
    });

    // insert iframe just after the loading indicator
    loadInd.after(plotIFrame);
    loadInd.after(closer);

    // write HTML to plot IFrame
    plotIFrame.contentWindow.document.open();
    // need DOCTYPE to avoid Firefox quirks mode
    plotIFrame.contentWindow.document.write("<!DOCTYPE HTML>");
    if(plotHTML != null){
        plotIFrame.contentWindow.document.write(plotHTML);
    }
    else{
        throw new Error("Date Range selected contains corrupted or missing data, please try another date.");
    }
    plotIFrame.contentWindow.document.close();

    loadInd.classList.add("visually-hidden");
}


// index specific event handlers
document.addEventListener('DOMContentLoaded', (event) => {
    // download indiv button
    const downloadButton = document.getElementById("download-data-button");
    if (downloadButton) {
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
    }

    //download all button
    const downloadAllButton = document.getElementById("downloadAllButton");
    if (downloadAllButton) {
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
        });
    }

    //plot button
    const plotButton = document.getElementById("plot-data-button");
    if (plotButton) {
        const currentDate = new Date();
        const timestamp = currentDate.getTime();
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

            // if the end date is in the future, return an error
            if (end.getTime() > timestamp) {
                const errString = "End date cannot be in the future.";
                window.modalSingleton.showModal(errString, () => { });
                return;
            }

            fetchPlot(sensors, start, end)
                .catch((err) => {
                    const errString = `An Error Ocurred: <br /> <br /> ${err}`;
                    window.modalSingleton.showModal(errString, () => { });
                });
        });
    }
});