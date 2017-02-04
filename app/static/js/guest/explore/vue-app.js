Vue.use(VueGoogleMap, {
    load: {
        key: 'AIzaSyAHdXg0Y_zk-wCNpslbBqcezLdHniaEwkI',
        v: '3',
        libraries: 'places'
    },
    installComponents: false
});

Vue.component('google-map', VueGoogleMap.Map);
Vue.component('map-marker', VueGoogleMap.Marker);

Vue.filter('tagCase', function (value) {
    return _.upperFirst(_.camelCase(value));
});

_.merge(window.placeholders, window.customPlaceholders);

//noinspection JSUnusedGlobalSymbols
var app = new Vue({
    el: '#explore',
    data: {
        resultsPerPage: window.resultsPerPage,
        location: window.locationName,
        events: window.events,
        filters: window.filters,
        currentPage: window.filters.hasOwnProperty('page') ? window.filters.page : 1,
        total: window.count,
        position: window.position,
        networkRequest: true,
        period: {
            from: moment().format('MM-DD-YYYY'),
            to: moment().format('MM-DD-YYYY')
        },
        shareUrl: ''
    },
    computed: {
        _: function () {
            return _;
        },
        zoom: function () {
            return this.position.lat === 0.0 && this.position.lng === 0.0 ? 1 : 15;
        },
        filterTags: function () {
            var filters = _.clone(this.filters);
            if (_.has(filters, 'query')) {
                delete filters['query'];
            }
            if (_.has(filters, 'page')) {
                delete filters['page'];
            }
            return filters;
        }
    },
    watch: {
        'location': function (value) {
            if (_.isEmpty(value.trim())) {
                this.position = {
                    lat: 0.0,
                    lng: 0.0
                };
            } else {
                var $this = this;
                geocodeAddress(window.geocoder, value, function (lat, lng) {
                    $this.position.lat = lat;
                    $this.position.lng = lng;
                }, false);
            }
            this.runFilter('location', value);
        }
    },
    methods: {
        isActive: function (type, value) {
            return _.get(this.filters, type, '') === value;
        },
        shouldExpand: function (type) {
            return _.get(this.filters, type, '') !== '';
        },
        runFilter: function (type, value, query) {
            app.networkRequest = true;
            value = _.trim(value);
            if (!_.isUndefined(query) && type != 'query') {
                if (query !== '') {
                    Vue.set(this.filters, 'query', query);
                } else {
                    Vue.delete(this.filters, 'query');
                }
            }
            if (type !== 'location' && value !== 'All Categories' && value !== 'All Event Types' && value !== 'All Dates' && value !== '') {
                Vue.set(this.filters, type, value);
                if (type == 'category') {
                    Vue.delete(this.filters, 'sub-category');
                }
            } else {
                Vue.delete(this.filters, type);
                if (value === 'All Categories') {
                    Vue.delete(this.filters, 'category');
                    Vue.delete(this.filters, 'sub-category');
                }
            }
            if (type === 'page' && (value === '1' || value === 1)) {
                Vue.delete(this.filters, type);
            }

            if (type == 'period' && value == 'custom') {
                value = this.period.from + ' to ' + this.period.to;
                Vue.set(this.filters, 'period', value);
            }
            var baseUrl = window.location.href.split('?')[0];
            var location = this.location.trim();
            if (type === 'location') {
                if (_.isEmpty(location)) {
                    baseUrl = '/explore/world/events/';
                } else {
                    baseUrl = '/explore/' + slugify(this.location) + '/events/';
                }
            }

            baseUrl = baseUrl + '?' + $.param(this.filters);
            history.replaceState(null, null, baseUrl);
            loadResults(function (events) {
                if (!_.isUndefined(events) && !_.isNull(events)) {
                    app.events = events;
                } else {
                    app.events = [];
                }
                app.networkRequest = false;
            });
        },
        removeTag: function (name) {
            this.runFilter(name, '');
        },
        recenterMap: function () {
            var center = window.map.getCenter();
            google.maps.event.trigger(window.map, 'resize');
            window.map.setZoom(window.map.getZoom());
            window.map.setCenter(center);
        },
        shareEvent: function (event) {
            var pathArray = location.href.split('/');
            var protocol = pathArray[0];
            var host = pathArray[2];
            var url = protocol + '//' + host;
            this.shareUrl = url + "/e/" + event.identifier + "/" + slugify(event.name);
            $("#share-modal").modal('show');
            setSocialLinks(this.shareUrl, event.name + ' - Powered by ' + window.appName);
        }
    },
    compiled: function () {

    }
});

app.$nextTick(function () {
    var $div = $(this.$el);
    explorerInit($div);
    this.networkRequest = false;
});
