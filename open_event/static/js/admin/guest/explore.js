/**
 * Created by Niranjan on 29-Jun-16.
 */

window.queryString = (function (a) {
    if (a == "") return {};
    var b = {};
    for (var i = 0; i < a.length; ++i) {
        var p = a[i].split('=', 2);
        if (p.length == 1)
            b[p[0]] = "";
        else
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
    }
    return b;
})(window.location.search.substr(1).split('&'));

function partSlugify(text) {
    return text.toString().toLowerCase()
        .replace(/\s+/g, '-')           // Replace spaces with -
        .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
        .replace(/\-\-+/g, '-')         // Replace multiple - with single -
        .replace(/^-+/, '')             // Trim - from start of text
        .replace(/-+$/, '');            // Trim - from end of text
}

function trimText(text) {
    return text.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function slugify(text) {
    var splitWord = text.split(",");
    _.forEach(splitWord, function (value, key) {
        splitWord[key] = partSlugify(value);
    });
    return splitWord.join('--');
}

$(document).on('click', '.filter-item', function () {
    var $filterItem = $(this);
    var type = $filterItem.parent().data('filter-type');
    if (type == "sub_category") {
        $filterItem.closest('.categories').find('.filter-item').removeClass('active');
    }
    if ($filterItem.hasClass('all-filter')) {
        $filterItem.parent().find('.filter-item').removeClass('active');
    }
    $filterItem.addClass('active');
    $filterItem.siblings().removeClass('active');
    runFilter(type, $filterItem.text())
});

var $locationField = $("#location");

$locationField.on('autocomplete', function () {
    runFilter('location', $locationField.val());
});

$("#location-search-form").submit(function (e) {
    e.preventDefault();
    runFilter('location', $locationField.val())
});

$("#event_browse").submit(function (e) {
    e.preventDefault();
    runFilter('query', $('#search-text').val());
});

$(document).on('click', '.filter-tag-btn', function (e) {
    e.preventDefault();
    var type = $(this).data('filter-type');
    runFilter(type, '');
    $(this).parent().remove();
});

function runFilter(type, value) {
    value = trimText(value);
    if (type !== 'location' && value !== 'All Categories' && value !== 'All Event Types' && value !== 'All Dates' && value !== '') {
        window.queryString[type] = value;
    } else {
        delete window.queryString[type];
    }

    if(type === 'location') {
        $(".location-name").text(value);
    }
    var baseUrl = window.location.href.split('?')[0];
    if (type === 'location') {
        baseUrl = '/explore/' + slugify(value) + '/events'
    }
    console.log(window.queryString);
    baseUrl = baseUrl + '?' + $.param(window.queryString);
    history.replaceState(null, null, baseUrl);
    loadResults();
}

function loadResults() {
    if(window.swagger_loaded) {

        

    }
}
