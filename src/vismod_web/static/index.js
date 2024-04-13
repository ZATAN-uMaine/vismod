

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
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}


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
        // date range picker
        const dateRangeSelector = document.getElementById('dateRange');
        if (!dateRangeSelector) {
            return;
        }

        const dateRangeInfo = document.querySelector('p.available-dates').textContent;

        // Extract available date range from the string written on the page

        const dataStart = new Date(dateRangeInfo.split("from")[1].split("to")[0]);
        const dataEnd = new Date(dateRangeInfo.split("to")[1].split(".")[0]);
        dataEnd.setDate(dataEnd.getDate());

        $(dateRangeSelector).daterangepicker({
            showDropdowns: true,
            timePicker: true,
            timePicker24Hour: true,
            autoApply: true,
            alwaysShowCalendars: true,
            startDate: this.startTime,
            endDate: this.endTime,
            opens: 'left',
            locale: {
                format: 'MMMM D, YYYY'
            },
            minDate: dataStart, // Set the minimum date to the start date of the dataset
            maxDate: dataEnd, // Set the maximum date to the end date of the dataset
            isInvalidDate: function (date) {
                // Check if the date is within the available data range
                return date < dataStart || date > dataEnd;
            },
        }, this.updateSelectedDate);

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
    updateSelectedDate(start, end) {
        if (start && end) {
            this.startTime = start.toDate();
            this.endTime = end.toDate();

            const startDateString = this.startTime.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            const endDateString = this.endTime.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            const dateRangeSelector = document.getElementById('dateRange');
            dateRangeSelector.value = `${startDateString} - ${endDateString}`;
        }
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
    try {
        plotHTML = await req.text();
    }
    catch {
        if (req.status == 500) {
            throw new Error("Date Range selected contains corrupted or missing data");
        }
        if (req.status != 200) {
            loadInd.classList.add("visually-hidden");
            throw new Error(await req.text());
        }
    }


    // create new iframe for plot
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

    // check if plotHTML is null or empty
    if (plotHTML ==
        "None" || plotHTML.trim() === '') {
        // create a smaller iframe or display a message
        plotIFrame.contentWindow.document.open();
        plotIFrame.contentWindow.document.write("<!DOCTYPE HTML>");
        plotIFrame.contentWindow.document.write("<div style='padding: 2.5rem; font-style: italic;'>No data available for the selected date range.</div>");
        plotIFrame.contentWindow.document.close();

        // adjust the height of the iframe
        plotIFrame.style.height = "100px";
    } else {
        // write HTML to plot IFrame
        plotIFrame.contentWindow.document.open();
        plotIFrame.contentWindow.document.write("<!DOCTYPE HTML>");
        plotIFrame.contentWindow.document.write(plotHTML);
        plotIFrame.contentWindow.document.close();

        // adjust the height of the iframe
        plotIFrame.style.height = "525px";
    }

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