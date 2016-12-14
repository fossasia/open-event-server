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
 */
function geocodeAddress(geocoder, address, callback) {
    geocoder.geocode({'address': address}, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            fillInAddress(callback, results[0].geometry.location.lat(), results[0].geometry.location.lng());
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

/**
 * Start stripe OAuth flow
 *
 * @param callback
 */
function stripeConnect(callback) {
    $.oauthpopup({
        path: window.stripeConnectUrl,
        callback: function () {
            // Disallow test accounts. Only accept live accounts.
            if (_.isUndefined(window.oauth_response)) {
                callback(false);
            } else {
                if (window.oauth_response.live_mode) {
                    callback(true, window.oauth_response);
                } else {
                    createSnackbar('Your stripe account is not live. Only live accounts can be used for collecting payments.');
                    callback(false);
                }
            }
        }
    });
}

/**
 * Apply a discount code
 *
 * @param discountCodeValue
 * @param callback
 */
function applyDiscountCode(discountCodeValue, callback) {
    $.post("/events/discount/apply", {
        discount_code: discountCodeValue
    }).done(function (data) {
        if (data.status === 'ok') {
            callback(data.discount_code.id, data.discount_code.value + "% over a period of " + data.discount_code.max_quantity + " month(s)");
        } else {
            var message = "An error occurred while trying to apply the discount code.";
            if (data.hasOwnProperty('message')) {
                message = data.message;
            }
            callback(null, message);
        }
    }).fail(function () {
        callback(null, "An error occurred while trying to apply the discount code.");
    });
}


