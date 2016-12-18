window.componentForm = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    administrative_area_level_1: 'short_name',
    country: 'long_name',
    postal_code: 'short_name'
};

/**
 * Convert address to latitude and longitude
 *
 * @param geocoder
 * @param address
 * @param callback
 * @param fillAddress
 */
function geocodeAddress(geocoder, address, callback, fillAddress) {
    if(_.isUndefined(fillAddress)) {
        fillAddress = true;
    }
    geocoder.geocode({'address': address}, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            var lat = results[0].geometry.location.lat(),
                lng = results[0].geometry.location.lng();
            if(fillAddress) {
                fillInAddress(callback, lat, lng);
            } else {
                callback(lat, lng);
            }
        } else {
            if (status === 'ZERO_RESULTS') {
                callback(0.0, 0.0);
            }
        }
    });
}

/**
 * Fill in address components
 *
 * @param callback
 * @param lat
 * @param lng
 */
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
