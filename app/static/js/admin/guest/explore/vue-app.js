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

Vue.filter('camel', function (value) {
    return _.camelCase(value);
});

_.merge(window.placeholders, window.customPlaceholders);

//noinspection JSUnusedGlobalSymbols
var app = new Vue({
    el: '#explore',
    data: {
        LIMIT_PER_PAGE: 10,
        location: window.locationName,
        events: window.events,
        filters: window.filters,
        currentPage: window.filters.hasOwnProperty('page') ? window.filters.page : 1,
        total: window.count,
        position: {
            lat: 0.0,
            lng: 0.0
        },
        networkRequest: true
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
            if(_.has(filters, 'query')) {
                delete filters['query'];
            }
            if(_.has(filters, 'page')) {
                delete filters['page'];
            }
            return filters;
        }
    },
    watch: {

    },
    methods: {
        runFilter: function (type, value) {
            app.networkRequest = true;
            value = _.trim(value);
            if (type !== 'location' && value !== 'All Categories' && value !== 'All Event Types' && value !== 'All Dates' && value !== '') {
                Vue.set(this.filters, type, value);
            } else {
                Vue.delete(this.filters, type);
                if (value === 'All Categories') {
                    Vue.delete(this.filters, 'category');
                }
            }
            if (type === 'page' && (value === '1' || value === 1)) {
                Vue.delete(this.filters, type);
            }

            var baseUrl = window.location.href.split('?')[0];
            if (type === 'location' && this.location != "") {
                baseUrl = '/explore/' + slugify(this.location) + '/events';
            }
            baseUrl = baseUrl + '?' + $.param(this.filters);
            history.replaceState(null, null, baseUrl);
            loadResults(function (events) {
                if( !_.isUndefined(events) && !_.isNull(events)) {
                    app.events = events;
                } else {
                    app.events = [];
                }
                app.networkRequest = false;
            });
        }
    },
    compiled: function () {

    }
});

app.$nextTick(function () {
    var $div = $(this.$el);
    explorerInit($div);
});
