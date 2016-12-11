window.componentForm = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    administrative_area_level_1: 'short_name',
    country: 'long_name',
    postal_code: 'short_name'
};

function geocodeAddress(geocoder, address, callback) {
    geocoder.geocode({'address': address}, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            fillInAddress(callback, results[0].geometry.location.lat(), results[0].geometry.location.lng());
        } else {
            if (status === 'ZERO_RESULTS') {
                callback(0.0, 0.0)
            }
            console.error('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function fillInAddress(callback, lat, lng) {
    var place = window.autocomplete.getPlace();
    if (!_.isUndefined(place) && place) {
        for (var i = 0; i < place.address_components.length; i++) {
            var addressType = place.address_components[i].types[0];
            if (componentForm[addressType]) {
                document.getElementById(addressType).value = place.address_components[i][componentForm[addressType]];
            }
        }
    }
    callback(lat, lng);
}
