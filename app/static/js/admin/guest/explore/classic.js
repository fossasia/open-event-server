/**
 * Convert text to UpperCamelCase
 * @param text
 */
function camelCase(text) {
    return _.upperFirst(_.camelCase(text));
}

function isImageInvalid(url) {
    if (_.isUndefined(url) || _.isNull(url) || _.isEmpty(url)) {
        return true;
    }
    url = trimText(url);
    return (url === 'null' || url === '' || url === ' ');
}

function filterHas(what) {
    return _.has(app.filters, what);
}

function getFilter(what) {
    return _.get(app.filters, what, '');
}

/**
 * Load results
 * @param [start] the start index to load from
 * @param page
 * @param callback
 */
function loadResults(start, page, callback) {
    if (isUndefinedOrNull(start)) {
        start = 1;
    }

    if (isUndefinedOrNull(page)) {
        page = 1;
    }

    initializeSwaggerClient(function () {

        var params = {
            start: start,
            limit: app.LIMIT_PER_PAGE,
            privacy: 'public',
            state: 'Published',
            location: app.location
        };

        if (filterHas('period')) {
            params['time_period'] = getFilter('period');
        }

        if (filterHas('page')) {
            params['start'] = ((parseInt(getFilter('page', 1)) - 1) * app.LIMIT_PER_PAGE) + 1;
        }

        if (filterHas('type')) {
            params['type'] = getFilter('type');
        }

        if (filterHas('category')) {
            params['topic'] = getFilter('category');
        }

        if (filterHas('query')) {
            params['contains'] = getFilter('query');
        }

        if (filterHas('sub-category')) {
            params['sub_topic'] = getFilter('sub-category');
        }

        api.events.get_event_list_paginated(params, function (response) {
            callback(response.obj.results);
        }, function (error) {
            if (error.status !== 404) {
                createSnackbar('An error occurred while retrieving your search results.');
            }
            callback(null);
        });
    });
}
