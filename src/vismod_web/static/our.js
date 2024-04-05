var selectedSensor = 'sensor2A' // default value
var selectedStartDay = ''
var selectedStartHour = ''
var selectedEndDay = ''
var selectedEndHour = ''

function updateDateRangeSelection() {
    selectedStartDay = document.getElementById('startDate').value
    selectedStartHour = document.getElementById('startHour').value
    selectedEndDay = document.getElementById('endDate').value
    selectedEndHour = document.getElementById('endHour').value
}

function createModal(sensorId, modal) {
    // update variables
    selectedSensor = sensorId
    updateDateRangeSelection()

    // inform user of selected sensor (rename later, probably)
    modalSensor = document.getElementById('modal-sensor')
    modalSensor.textContent = `${selectedSensor}`

    // inform user of selected range
    modalRange = document.getElementById('modal-range')
    modalRange.textContent = `(${selectedStartDay}, ${selectedStartHour}:00) to (${selectedEndDay}, ${selectedEndHour}:00)`

    // show modal popup
    modal.style.display = 'block'
}

function createPlotIFrame(htmlcode) {
    console.log('ZALGO')
    const plotIFrame = document.createElement('iframe')
    // plotIFrame.srcdoc = src

    // var htmlcode = `
    // <body><h1 style="text-align: center; color: green;"}>Plot of ${selectedSensor}'s data from ${selectedStartHour}:00 on ${selectedStartDay} to ${selectedEndHour}:00 on ${selectedEndDay}</h1></body>
    // `

    plotIFrame.setAttribute('scrolling', 'no')
    plotIFrame.setAttribute('style', 'border:none;')
    plotIFrame.setAttribute('seamless', 'seamless')
    plotIFrame.setAttribute('height', '525')
    plotIFrame.setAttribute('width', '100%')

    document.getElementById('plotBay').appendChild(plotIFrame)
    
    plotIFrame.contentWindow.document.open()
    plotIFrame.contentWindow.document.write(htmlcode)
    plotIFrame.contentWindow.document.close()

    var modal = document.getElementById('myModal')
    modal.style.display = 'none'
}

document.addEventListener('DOMContentLoaded', (event) => {
    // Set default dates
    const now = new Date()
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const minDate = '2023-08-01' // TODO: fix later to actual minimum date

    const formatDate = (date) => {
        const year = date.getFullYear()
        const month = (date.getMonth() + 1).toString().padStart(2, '0')
        const day = date.getDate().toString().padStart(2, '0')
        return `${year}-${month}-${day}`
    }

    const startDaySelector = document.getElementById('startDate')
    const endDaySelector = document.getElementById('endDate')
    const startHourSelector = document.getElementById('startHour')
    const endHourSelector = document.getElementById('endHour')

    startDaySelector.setAttribute('min', minDate)
    startDaySelector.setAttribute('max', formatDate(now))
    endDaySelector.setAttribute('min', minDate)
    endDaySelector.setAttribute('max', formatDate(now))

    // Populate the hour <select> elements
    for (let i = 0; i < 24; i++) {
        const hourValue = i.toString().padStart(2, '0') + ':00'
        const option = new Option(hourValue, i)
        startHourSelector.add(option.cloneNode(true))
        endHourSelector.add(option.cloneNode(true))
    }

    // Set default values for dates
    startDaySelector.value = formatDate(oneWeekAgo)
    endDaySelector.value = formatDate(now)

    // Set default values for hours
    startHourSelector.value = oneWeekAgo.getHours()
    endHourSelector.value = now.getHours()

    // Enforce date constraints
    startDaySelector.max = endDaySelector.value
    endDaySelector.min = startDaySelector.value

    // Enforce time constraints
    const enforceTimeConstraints = () => {
        const startHour = parseInt(startHourSelector.value, 10)
        const endHour = parseInt(endHourSelector.value, 10)
        if (
            startDaySelector.value === endDaySelector.value &&
            startHour > endHour
        ) {
            endHourSelector.value = startHour
        }
    }

    updateDateRangeSelection()

    startDaySelector.addEventListener('change', function () {
        endDaySelector.min = this.value
        enforceTimeConstraints()
        updateDateRangeSelection()
    })

    endDaySelector.addEventListener('change', function () {
        startDaySelector.max = this.value
        enforceTimeConstraints()
        updateDateRangeSelection()
    })

    startHourSelector.addEventListener('change', function () {
        enforceTimeConstraints()
        updateDateRangeSelection()
    })

    endHourSelector.addEventListener('change', function () {
        enforceTimeConstraints()
        updateDateRangeSelection()
    })

    // Get the modal
    var modal = document.getElementById('myModal')

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName('close')[0]

    // Toggles dark mode + sun mode and hides/shows the appropriate icon
    var themeToggle = document.getElementById('theme-toggle')

    // const circles = document.querySelectorAll('[id^="sensor"]')
    const circles = document.querySelectorAll('.sensor')

    circles.forEach((circle) => {
        circle.addEventListener('click', () => createModal(circle.id, modal))
    })

    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = 'none'
    }

    themeToggle.onclick = function () {
        document.body.classList.toggle("dark")
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = 'none'
        }
    }
})

function requestCSV(all_sensors=false) { 
    let dataSensor = selectedSensor
    if(all_sensors){
        dataSensor = 'all'
    }
    alert("The creation and subsequent download of your csv will occur after you click \"OK\". \nBy clicking \"OK\", you acknowledge that the data downloaded does not reflect the structual integrity of the Penobscot Narrows Bridge.")
    $.ajax({ 
        url: '/download_csv', 
        type: 'GET', 
        data: { 
            'sensor'    :   dataSensor,
            'startDay'  :   selectedStartDay,
            'startHour' :   selectedStartHour,
            'endDay'    :   selectedEndDay,
            'endHour'   :   selectedEndHour
        }, 
        success: function(response) { 
            console.log("CSV INCOMING");
            // console.log(response)
            const blob = new Blob([response], {type: 'text/csv'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'data.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }, 
        error: function(error) { 
            console.log("ERROR INCOMING")
            console.log(error); 
        } 
    }); 
} 

function requestPlot() {
    alert("The creation and subsequent download of your plot will occur after you click \"OK\". \nBy clicking \"OK\", you acknowledge that the data downloaded does not reflect the structual integrity of the Penobscot Narrows Bridge.")
    $.ajax({ 
        url: '/display_plot', 
        type: 'GET', 
        data: { 
            'sensor'    :   selectedSensor,
            'startDay'  :   selectedStartDay,
            'startHour' :   selectedStartHour,
            'endDay'    :   selectedEndDay,
            'endHour'   :   selectedEndHour
        }, 
        success: function(response) { 
            console.log("mazel_tav");
            // const plotContainer = document.createElement('div')
            // plotContainer.innerHTML = response
            // document.getElementById('plotBay').appendChild(plotContainer)
            createPlotIFrame(response)
        }, 
        error: function(error) { 
            console.log("ERROR INCOMING")
            console.log(error); 
        } 
    }); 
}