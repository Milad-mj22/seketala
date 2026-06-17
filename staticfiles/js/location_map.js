// Wait until the document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the map centered at a default location (latitude, longitude)
    var map = L.map('map').setView([35.6895, 51.3890], 13);  // Default to Tehran, Iran

    // Load the map tiles from OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add a marker for the current location
    var marker = L.marker([35.6895, 51.3890]).addTo(map);

    // Function to update latitude and longitude input fields
    function updateLatLon(lat, lon) {
        document.getElementById('id_latitude').value = lat;
        document.getElementById('id_longitude').value = lon;
    }

    // On map click, move the marker and update the inputs
    map.on('click', function(e) {
        var lat = e.latlng.lat;
        var lon = e.latlng.lng;

        marker.setLatLng([lat, lon]);
        updateLatLon(lat, lon);
    });

    // Initialize with the existing location if available
    var latField = document.getElementById('id_latitude').value;
    var lonField = document.getElementById('id_longitude').value;
    if (latField && lonField) {
        var lat = parseFloat(latField);
        var lon = parseFloat(lonField);
        map.setView([lat, lon], 13);
        marker.setLatLng([lat, lon]);
    }
});
