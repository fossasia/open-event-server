/**
 * Created by Niranjan on 14-Jun-16.
 */
var $eventBrowseForm = $("#event_browse");
var $searchTextBox = $eventBrowseForm.find('#search-text');
var $locationField = $eventBrowseForm.find('input[name=location]');
var $categoryField = $eventBrowseForm.find('input[name=category]');
$(document).ready(function () {
    $('.search-button').click(function (e) {
        if (window.innerWidth <= 711 && ($searchTextBox.val() == "")) {
            e.preventDefault();
            $searchTextBox.toggle();
            $searchTextBox.width(0.8 * window.innerWidth);
        }
    });

    var locationRequestUrl = "/api/location/";
    $.ajax({
        url: locationRequestUrl,
        type: 'POST',
        success: function (json) {
            $("#location").val(json.name);
            $locationField.val(json.name);
            initializeSearchAutoComplete(json.name);
        },
        error: function (err) {
            console.log("Request failed, error= " + err);
        }
    });

});

function initializeSearchAutoComplete(location_slug) {
    var locations = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
            url: '/explore/autocomplete/locations.json',
            cache: false
        }
    });

    var categories = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
            url: '/explore/autocomplete/categories.json',
            cache: false
        }
    });

    var events = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
            url: '/explore/autocomplete/events/' + location_slug + '.json',
            cache: false
        }
    });

    $searchTextBox.typeahead({
        highlight: true
    }, {
        name: 'events',
        display: 'value',
        source: events
    }, {
        name: 'locations',
        source: locations,
        display: 'value',
        templates: {
            header: '<h5 class="data-set-title">Locations</h5>'
        }
    }, {
        name: 'categories',
        source: categories,
        display: 'value',
        templates: {
            header: '<h5 class="data-set-title">Categories</h5>'
        }
    });

    $searchTextBox.bind('typeahead:select', function (ev, suggestion) {
        var $targetField = $searchTextBox;
        switch (suggestion.type) {
            case 'category':
                $targetField = $categoryField;
                break;
            case 'location':
                $targetField = $locationField;
                break;
        }
        $targetField.val(suggestion.value);
        $eventBrowseForm.submit();
    });
}

function handleDataTablePagination($table) {
    var $paginator = $table.closest(".dataTables_wrapper").find(".dataTables_paginate");
    if($paginator.find(".paginate_button").length > 3) {
        $paginator.show();
    } else {
        $paginator.hide();
    }
}

$(function () {
    var $tables = $("table.dataTable");
    $tables.on('draw.dt', function () {
        handleDataTablePagination($(this))
    });
    handleDataTablePagination($tables);
});
