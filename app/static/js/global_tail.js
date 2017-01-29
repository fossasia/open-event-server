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
        error: function (err) { }
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
    if ($paginator.find(".paginate_button").length > 3) {
        $paginator.show();
    } else {
        $paginator.hide();
    }
}

$(function () {
    var $tables = $("table.dataTable");
    $tables.on('draw.dt', function () {
        handleDataTablePagination($(this));
    });
    handleDataTablePagination($tables);
});

$(".lang-list").on('click', '.translate', function () {
    var l_code = $(this).attr("id");
    var request_url = window.location.protocol + "//" + window.location.host + "/choose_language/";
    $.ajax({
        type: 'POST',
        url: request_url,
        data: {"l_code": l_code},
        success: function (data) {
            if (data === l_code) {
                location.reload();
            }
        }
    });
});


function setATagsInNotifMenuDropDown(notificationViewPath) {
    $('ul#notif-menu li.notif-menu-li').each(function (i, li) {
        $(li).children("a").children(".message").click(function () {
            window.location = notificationViewPath;
        });
        $(li).children("a").children(".mark-as-read").click(function () {
            var url = $(this).data("markread");
            var $notifCount = $("#notif_count");
            $.ajax({
                url: url,
                success: function (data) {
                    $(li).slideUp(500, function () {
                        $(li).remove();
                    });
                    var notif_count = $notifCount.text();
                    $notifCount.text(parseInt(notif_count) - 1);
                }
            });
        });
    });
}

$(document).ready(function () {

    var $megaDropdown = $('li.dropdown.mega-dropdown');

    $('li.dropdown.mega-dropdown a').on('click', function (event) {
        $(this).parent().toggleClass('open');
    });
    $('body').on('click', function (e) {
        if (!$megaDropdown.is(e.target) && $megaDropdown.has(e.target).length === 0 && $('.open').has(e.target).length === 0) {
            $('li.dropdown.mega-dropdown').removeClass('open');
        }
    });

    // Add event handler to Mark-all-read notification button
    $(".notif-mark-all-read").click(function (e) {
        e.preventDefault();
        var url = $(this).data("markallread");
        $.ajax({
            url: url,
            success: function (data) {
                $("ul#notif-menu li.notif-menu-li").each(function (i, li) {
                    $(li).slideUp(500, function () {
                        $(li).remove();
                    });
                    $("#notif_count").text("");
                });
            }
        });
    });
});
