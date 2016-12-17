function explorerInit($div) {
    /*var $customDateCollapse = $div.find('#custom-date-collapse');
     $customDateCollapse.find('.date').datepicker({
     'format': 'mm-dd-yyyy',
     'autoclose': true
     });
     new Datepair($customDateCollapse[0], {
     'defaultDateDelta': 1
     });*/
    $("#event_browse").submit(function (e) {
        e.preventDefault();
        app.runFilter('query', $('#search-text').val());
    }).bind('typeahead:select', function (ev, suggestion) {
        ev.preventDefault();
        switch (suggestion.type) {
            case 'category':
                app.runFilter('category', suggestion.value);
                break;
            case 'location':
                app.runFilter('location', suggestion.value);
                break;
            default:
                app.runFilter('query', suggestion.value);
        }
    });
}

VueGoogleMap.loaded.then(function () {
/*    window.geocoder = new google.maps.Geocoder();
    var locationInput = $("#location_name")[0];
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
            }
        } catch (ignored) {
        }
    }, 100);*/
});
