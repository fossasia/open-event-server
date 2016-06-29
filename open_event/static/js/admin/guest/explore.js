/**
 * Created by Niranjan on 29-Jun-16.
 */

var LIMIT_PER_PAGE = 10;

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

function camelCase(text) {
    return _.upperFirst(_.camelCase(text));
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

    if (type === 'location') {
        $(".location-name").text(value);
    }
    var baseUrl = window.location.href.split('?')[0];
    if (type === 'location') {
        baseUrl = '/explore/' + slugify(value) + '/events'
    }
    baseUrl = baseUrl + '?' + $.param(window.queryString);
    history.replaceState(null, null, baseUrl);
    loadResults();
}

function queryHas(param) {
    return window.queryString.hasOwnProperty(param)
}

function getQuery(param) {
    return window.queryString[param];
}

var eventTemplate = $("#event-template").html();
var filterTagTemplate = $("#filter-tag-template").html();
var $filterTagsHolder = $(".filtering");
var $eventsHolder = $("#events-holder");

function addFilterTag(type, value) {
    var $tag = $(filterTagTemplate);
    $tag.find(".value").text(value);
    $tag.find(".filter-tag-btn").attr("data-filter-type", type);
    $filterTagsHolder.append($tag);
}

function addEvent(event) {
    var $eventElement = $(eventTemplate);
    $eventElement.find("a").attr("href", "/e/" + event.id);
    $eventElement.find(".event-image").attr('src', event.background_url);
    $eventElement.find(".name").text(event.name);
    $eventElement.find(".location_name").text(event.location_name.split(",")[0]);
    $eventElement.find(".share-btn").attr("data-event-id", event.id).attr("data-title", event.name);
    $eventElement.find(".time").text(moment(event.start_time).format('ddd, MMM DD HH:mm A'));
    var tags = "";
    if (!_.isEmpty(event.type)) {
        tags += " #" + camelCase(event.type);
    }

    if (!_.isEmpty(event.topic)) {
        tags += " #" + camelCase(event.topic);
    }
    $eventElement.find(".tags").prepend(tags);
    $eventsHolder.append($eventElement);
}

function loadResults(start) {

    if (isUndefinedOrNull(start)) {
        start = 1
    }

    $filterTagsHolder.html('');
    initializeSwaggerClient(function () {

        var params = {
            start: start,
            limit: LIMIT_PER_PAGE,
            privacy: 'public',
            state: 'Published',
            location: $locationField.val()
        };

        if (queryHas('period')) {
            params['time_period'] = getQuery('period');
            addFilterTag('period', getQuery('period'))
        }

        if (queryHas('type')) {
            params['type'] = getQuery('type');
            addFilterTag('type', getQuery('type'))
        }

        if (queryHas('query')) {
            params['contains'] = getQuery('query');
        }

        if (queryHas('sub-category')) {
            params['sub_topic'] = getQuery('sub-category');
            addFilterTag('sub-category', getQuery('sub-category'))
        }

        api.events.get_event_list_paginated(params, function (response) {
            $eventsHolder.html("");
            response = response.obj;
            _(response.results).forEach(function (event) {
                addEvent(event);
            });
        })
    });
}
