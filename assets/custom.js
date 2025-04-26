// custom.js
window.onload = function() {
    // Initialize any additional JavaScript functionality or interactive elements

    // Example: Adding click event listeners to map markers
    document.querySelectorAll('.leaflet-marker-icon').forEach(function(marker) {
        marker.addEventListener('click', function() {
            alert("You clicked a marker!");
        });
    });

    // Example: Log when dropdown value changes (you can extend this logic)
    document.querySelector('#severity-dropdown').addEventListener('change', function(e) {
        console.log('Selected severity: ' + e.target.value);
    });
};
