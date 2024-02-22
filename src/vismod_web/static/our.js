var current_sensor = "sensor1";

function updateSensor(sensorId, modal) {
    current_sensor = sensorId;

    which_sensor = document.getElementById("which-sensor");
    which_sensor.textContent = `${current_sensor}`;

    which_range = document.getElementById("which-range");
    

    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const startHourSelect = document.getElementById('startHour');
    const endHourSelect = document.getElementById('endHour');

    which_range.textContent = `(${startDateInput.value}, ${startHourSelect.value}:00) to (${endDateInput.value}, ${endHourSelect.value}:00)`;

    modal.style.display = "block";
}


// because of the way JS works, all of these vars are available out of scope. lol how did i not know that.
document.addEventListener('DOMContentLoaded', (event) => { 
    // Set default dates
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
    const minDate = "2023-08-01"; // just a guess, will fix later

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const startHourSelect = document.getElementById('startHour');
    const endHourSelect = document.getElementById('endHour');

    startDateInput.setAttribute('min', minDate);
    startDateInput.setAttribute('max', formatDate(now));
    endDateInput.setAttribute('min', minDate);
    endDateInput.setAttribute('max', formatDate(now));

    // Populate the hour <select> elements
    for (let i = 0; i < 24; i++) {
        const hourValue = i.toString().padStart(2, '0') + ':00';
        const option = new Option(hourValue, i);
        startHourSelect.add(option.cloneNode(true));
        endHourSelect.add(option.cloneNode(true));
    }

    // Set default values for dates
    startDateInput.value = formatDate(oneWeekAgo);
    endDateInput.value = formatDate(now);

    // Set default values for hours
    startHourSelect.value = oneWeekAgo.getHours();
    endHourSelect.value = now.getHours();

    // Enforce date constraints
    startDateInput.max = endDateInput.value;
    endDateInput.min = startDateInput.value;

    // Enforce time constraints
    const enforceTimeConstraints = () => {
        const startHour = parseInt(startHourSelect.value, 10);
        const endHour = parseInt(endHourSelect.value, 10);
        if (startDateInput.value === endDateInput.value && startHour > endHour) {
            endHourSelect.value = startHour;
        }
    };

    startDateInput.addEventListener('change', function () {
        endDateInput.min = this.value;
        enforceTimeConstraints();
    });

    endDateInput.addEventListener('change', function () {
        startDateInput.max = this.value;
        enforceTimeConstraints();
    });

    startHourSelect.addEventListener('change', function () {
        enforceTimeConstraints();
    });

    endHourSelect.addEventListener('change', function () {
        enforceTimeConstraints();
    });


    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    const circles = document.querySelectorAll('[id^="sensor"]');
    circles.forEach(circle => {
        circle.addEventListener('click', () => updateSensor(circle.id, modal))
    });

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
    modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
    }
});
