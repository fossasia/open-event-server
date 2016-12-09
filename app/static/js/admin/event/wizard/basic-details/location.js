    var marker, map;
    var init_marker;
    var placeSearch, autocomplete;
    var paid_tickets = 0;
    var componentForm = {
        street_number: 'short_name',
        route: 'long_name',
        locality: 'long_name',
        administrative_area_level_1: 'short_name',
        country: 'long_name',
        postal_code: 'short_name'
    };
    var $latitudeInput = $('#latitude');
    var $longitudeInput = $('#longitude');
    var $locationInput = $("#location_name");

    function initPlacesApi() {
        var latitude = $latitudeInput.val();
        var longitude = $longitudeInput.val();
        var latlng = new google.maps.LatLng(latitude, longitude);
        map = new google.maps.Map($("#map")[0], {
            zoom: 1,
            center: latlng
        });

        var geocoder = new google.maps.Geocoder();
        init_marker = new google.maps.Marker({
            draggable: true,
            position: latlng,
            map: map,
            zoom: 15
        });

        var geocodeHandler = function () {
            $locationInput.closest(".form-group").removeClass("has-warning");
            geocodeAddress(geocoder, map);
        };

        $locationInput.valueChange(geocodeHandler);

        autocomplete = new google.maps.places.Autocomplete($locationInput[0], {types: ['geocode']});
        geolocate();

        autocomplete.addListener('place_changed', geocodeHandler);

    }
    function fillInAddress(map) {
        // Get the place details from the autocomplete object.
        var place = autocomplete.getPlace();
        // Get each component of the address from the place details
        // and fill the corresponding field on the form.

        for (var i = 0; i < place.address_components.length; i++) {
            var addressType = place.address_components[i].types[0];
            if (componentForm[addressType]) {
                console.log(addressType);
                document.getElementById(addressType).value = place.address_components[i][componentForm[addressType]];
            }
        }
        $locationInput.hide();
        $('#show_addr').hide();
        $('#map-holder').show();
        resizeMap(map);
    }

    function resizeMap(map) {
        var center = map.getCenter();
        google.maps.event.trigger(map, 'resize');
        map.setZoom(map.getZoom());
        map.setCenter(center);
    }

    function geocodeAddress(geocoder, resultsMap) {
        var address = $locationInput.val();
        geocoder.geocode({'address': address}, function (results, status) {
            if (status === google.maps.GeocoderStatus.OK) {
                $latitudeInput.val(results[0].geometry.location.lat());
                $longitudeInput.val(results[0].geometry.location.lng());
                resultsMap.setCenter(results[0].geometry.location);
                resultsMap.setZoom(10);
                init_marker.setMap(null);
                if (marker == null) {
                    marker = new google.maps.Marker({
                        map: resultsMap,
                        draggable: true,
                        position: results[0].geometry.location
                    });
                }
                else {
                    marker.setMap(null);
                    marker = new google.maps.Marker({
                        map: resultsMap,
                        draggable: true,
                        position: results[0].geometry.location
                    });
                }
                fillInAddress(resultsMap);
            } else {
                if (status === 'ZERO_RESULTS') {
                    resultsMap.setZoom(1);
                    $latitudeInput.val(0.0);
                    $longitudeInput.val(0.0);
                }
                console.log('Geocode was not successful for the following reason: ' + status);
            }
        });
    }

    function geolocate() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var geolocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                var circle = new google.maps.Circle({
                    center: geolocation,
                    radius: position.coords.accuracy
                });
                autocomplete.setBounds(circle.getBounds());
            });
        }
    }

    function show_map_holder() {
        if ($locationInput.get(0).value != '') {
            var url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + $locationInput.get(0).value + "&key=AIzaSyAHdXg0Y_zk-wCNpslbBqcezLdHniaEwkI"
            $.getJSON(url, function (data) {
                google.maps.event.trigger(autocomplete, 'place_changed');
                var place = data.results[0];
                for (var i = 0; i < place.address_components.length; i++) {
                    var addressType = place.address_components[i].types[0];
                    if (componentForm[addressType]) {
                        console.log(addressType);
                        document.getElementById(addressType).value = place.address_components[i][componentForm[addressType]];
                    }
                }
            });
        }
        $locationInput.hide();
        $('#map-holder').show();
        $('#show_addr').hide();
        resizeMap(map);
    }

    function remove_map_holder() {
        for (var component in componentForm) {
            document.getElementById(component).value = '';
        }
        autocomplete.set('place', void(0));
        $locationInput.get(0).value = '';
        $locationInput.show();
        $('#map-holder').hide();
        $('#show_addr').show();
    }

    function address_update() {
        autocomplete.set('place', void(0));
        var location = "";
        for (var component in componentForm) {
            location += $('#' + component).get(0).value + " ";
        }
        $locationInput.get(0).value = location;
        $locationInput.click();
    }

