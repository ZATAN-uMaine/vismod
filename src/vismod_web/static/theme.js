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
  DarkReader.setFetchMethod(window.fetch);
  if (DarkReader.isEnabled()) {
    disableDarkMode();
  } else {
    enableDarkMode();
  }
}


function enableDarkMode() {
  DarkReader.setFetchMethod(window.fetch);
  DarkReader.enable({
    brightness: 100,
    contrast: 100,
    sepia: 0
  });
  localStorage.setItem('darkModeEnabled', 'true');

  // Add dark mode class to daterangepicker
  const dateRangePicker = document.querySelector('.daterangepicker');
  if (dateRangePicker) {
    dateRangePicker.classList.add('daterangepicker-dark');
  }

}

function disableDarkMode() {
  DarkReader.disable();
  localStorage.setItem('darkModeEnabled', 'false');

  // Remove dark mode class from daterangepicker
  const dateRangePicker = document.querySelector('.daterangepicker');
  if (dateRangePicker) {
    dateRangePicker.classList.remove('daterangepicker-dark');
  }

}