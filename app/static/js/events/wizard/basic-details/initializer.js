if(!_.isUndefined(window.seed) && !_.isNull(window.seed.event)) {
    _.mergeWith(EVENT, window.seed.event, function (objectValue, sourceValue) {
        if(_.isUndefined(sourceValue) || _.isNull(sourceValue)) {
            return objectValue;
        }
    });
}

function basicDetailsInit($eventDiv) {
    /* Bind datepicker to dates */
    $eventDiv.find("input.date").datepicker({
        'format': 'mm/dd/yyyy',
        'autoclose': true
    }).on('changeDate', function () {
        this.dispatchEvent(new Event('input'));
    });
    $eventDiv.find("input.time").timepicker({
        'showDuration': true,
        'timeFormat': 'H:i',
        'scrollDefault': 'now'
    }).on('changeTime', function () {
        this.dispatchEvent(new Event('input'));
    });
    $eventDiv.find(".event-date-picker").datepair({
        'defaultTimeDelta': 3600000
    }).on('rangeSelected', function () {
        _.each($(this).find('input.date, input.time'), function (element) {
            element.dispatchEvent(new Event('input'));
        });
    });
    $eventDiv.find("textarea.event-textarea").summernote(summernoteConfig);
    $eventDiv.find(".licence-help").click(function () {
        $("#licence-list").slideToggle();
    });

}

VueGoogleMap.loaded.then(function () {
    window.geocoder = new google.maps.Geocoder();
    var locationInput = $("#location_name")[0];
    window.autocomplete = new google.maps.places.Autocomplete(locationInput, {types: ['geocode']});
    window.autocomplete.addListener('place_changed', function () {
        locationInput.dispatchEvent(new Event('input'));
        locationInput.dispatchEvent(new Event('gmap'));
    });

    var intervalID = setInterval(function () {
        try {
            if (!_.isUndefined(app.$refs.gmap.$mapObject)) {
                clearInterval(intervalID);
                window.map = app.$refs.gmap.$mapObject;
                app.recenterMap();
                app.mapLoaded = true;
            }
        } catch (ignored) {
        }
    }, 100);
});
