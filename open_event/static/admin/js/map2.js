  var map = L.map('map').setView([37.804146, -122.275045], 16);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    }).addTo(map);
    var geocoder = L.control.geocoder('XOnuJD0 ').addTo(map);
