// custom.js
window.onload = function() {

    document.querySelectorAll('.leaflet-marker-icon').forEach(function(marker) {
        marker.addEventListener('click', function() {
            alert("You clicked a marker!");
        });
    });

    document.querySelector('#severity-dropdown').addEventListener('change', function(e) {
        console.log('Selected severity: ' + e.target.value);
    });
};
