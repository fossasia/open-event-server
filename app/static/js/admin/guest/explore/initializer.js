function explorerInit($div) {
    var $customDateCollapse = $div.find('#custom-date-collapse');
    $customDateCollapse.find('.date').datepicker({
        'format': 'mm-dd-yyyy',
        'autoclose': true
    }).on('changeDate', function () {
        this.dispatchEvent(new Event('input'));
    });

    $customDateCollapse.datepair({
        'defaultDateDelta': 1
    }).on('rangeSelected', function () {
        _.each($(this).find('input.date'), function (element) {
            element.dispatchEvent(new Event('input'));
        });
    });

    var $eventBrowse = $("#event_browse");
    var $searchText = $("#search-text");
    $searchText.val(_.get(window.filters, 'query', ''));
    $eventBrowse.submit(function (e) {
        e.preventDefault();
        app.runFilter('query', $('#search-text').val());
    }).bind('typeahead:select', function (ev, suggestion) {
        ev.preventDefault();
        switch (suggestion.type) {
            case 'category':
                app.runFilter('category', suggestion.value, '');
                $searchText.val('');
                break;
            case 'location':
                app.runFilter('location', suggestion.value, '');
                $searchText.val('');
                break;
            default:
                app.runFilter('query', suggestion.value);
        }
    });
}

VueGoogleMap.loaded.then(function () {
    window.geocoder = new google.maps.Geocoder();
    var locationInput = $("#location-search")[0];
    window.autocomplete = new google.maps.places.Autocomplete(locationInput, {types: ['geocode']});
    window.autocomplete.addListener('place_changed', function () {
        locationInput.dispatchEvent(new Event('input'));
    });
    var intervalID = setInterval(function () {
        try {
            if (!_.isUndefined(app.$refs.gmap.$mapObject)) {
                clearInterval(intervalID);
                window.map = app.$refs.gmap.$mapObject;
                app.recenterMap();
                app.mapLoaded = true;
                initMapButtons();
            }
        } catch (ignored) {
        }
    }, 100);
});


function initMapButtons() {
    var centerControlDiv = document.createElement('div');
    new CenterControl(centerControlDiv, window.map);
    centerControlDiv.index = 1;
    window.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(centerControlDiv);

}

function CenterControl(controlDiv) {
    // Set CSS for the control border.
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = '#fff';
    controlUI.style.border = '2px solid #fff';
    controlUI.style.borderRadius = '3px';
    controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
    controlUI.style.cursor = 'pointer';
    controlUI.style.marginBottom = '5px';
    controlUI.style.textAlign = 'center';
    controlUI.title = 'Search this Area';
    controlDiv.appendChild(controlUI);

    // Set CSS for the control interior.
    var controlText = document.createElement('div');
    controlText.style.color = 'rgb(25,25,25)';
    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '12px';
    controlText.style.lineHeight = '38px';
    controlText.style.paddingLeft = '5px';
    controlText.style.paddingRight = '5px';
    controlText.innerHTML = 'Search this Area';
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to Chicago.
    controlUI.addEventListener('click', function () {
        geocoder.geocode({'location': window.map.getCenter()}, function (results, status) {
            if (status === google.maps.GeocoderStatus.OK) {
                var address;
                if (map.getZoom() > 4) {
                    address = results[1].formatted_address.replace(/[0-9]/g, '');
                } else {
                    address = results[results.length - 1].formatted_address.replace(/[0-9]/g, '');
                }
                app.location = address;
            } else {
                app.location = '';
            }
        });
    });

}
