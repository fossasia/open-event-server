if(!_.isUndefined(window.seed) && !_.isNull(window.seed.event)) {
    _.mergeWith(EVENT, window.seed.event, function (objectValue, sourceValue) {
        if(_.isUndefined(sourceValue) || _.isNull(sourceValue)) {
            return objectValue;
        }
    });
}

//noinspection JSUnusedGlobalSymbols
var basicDetailsApp = new Vue({
    el: '#event-wizard-basic-details',
    data: {
        event: EVENT,
        included_items: included_settings,
        addressShown: false,
        mapLoaded: false,
        discountMessage: {
            success: '',
            error: '',
            loading: false
        }
    },
    computed: {
        _: function () {
            return _;
        },
        subTopics: function () {
            if (_.isNull(this.event.topic)) {
                return []
            }
            return sub_topics[this.event.topic]
        },
        location: function () {
            return {
                lat: this.event.latitude,
                lng: this.event.longitude
            }
        },
        zoom: function () {
            return this.event.latitude == 0.0 && this.event.longitude == 0.0 ? 1 : 15
        }
    },
    watch: {
        'event.topic': function () {
            this.event.sub_topic = '';
        },
        'event.ticket_include': function () {
            this.event.tickets = [];
        },
        'addressShown': function (val) {
            if (val) {
                var $this = this;
                setTimeout(function () {
                    $this.recenterMap();
                }, 500);
            }
        },
        'event.location_name': function (val) {
            var $this = this;
            geocodeAddress(window.geocoder, val, function (lat, lng) {
                if (val.trim() != "") {
                    $this.addressShown = true;
                }
                $this.event.latitude = lat;
                $this.event.longitude = lng;
            });
        },
        'event.discount_code': function (val) {
            this.discountMessage.success = '';
            this.discountMessage.error = '';
        }
    },
    methods: {
        addSocialLink: function () {
            this.event.social_links.push(_.clone(SOCIAL_LINK));
        },
        removeSocialLink: function (socialLink) {
            var index = this.event.social_links.indexOf(socialLink);
            this.event.social_links.splice(index, 1);
        },
        removeTicket: function (ticket) {
            if (confirm("Are you sure you want to remove this ticket ?")) {
                var index = this.event.tickets.indexOf(ticket);
                this.event.tickets.splice(index, 1);
            }
        },
        addTicket: function (ticketType) {
            var ticket = _.cloneDeep(TICKET);
            ticket.type = ticketType;
            this.event.tickets.push(ticket);
        },
        recenterMap: function () {
            var center = window.map.getCenter();
            google.maps.event.trigger(window.map, 'resize');
            window.map.setZoom(window.map.getZoom());
            window.map.setCenter(center);
        },
        updateAddress: function () {
            var locationName = "";
            for (var component in window.componentForm) {
                locationName += $('#' + component).get(0).value + " ";
            }
            this.event.location_name = locationName;
        },
        connectToStripe: function () {
            var $this = this;
            stripeConnect(function (status, response) {
                $this.event.stripe.linked = status;
                if (status) {
                    $this.event.stripe.stripe_secret_key = response.access_token;
                    $this.event.stripe.stripe_refresh_token = response.refresh_token;
                    $this.event.stripe.stripe_publishable_key = response.stripe_publishable_key;
                    $this.event.stripe.stripe_user_id = response.stripe_user_id;
                    $this.event.stripe.stripe_email = response.email;
                }
            });
        },
        disconnectFromStripe: function () {
            $this.event.stripe.linked = false;
            $this.event.stripe.stripe_secret_key = '';
            $this.event.stripe.stripe_refresh_token = '';
            $this.event.stripe.stripe_publishable_key = '';
            $this.event.stripe.stripe_user_id = '';
            $this.event.stripe.stripe_email = '';
        },
        applyDiscount: function () {
            var $this = this;
            $this.discountMessage.loading = true;
            applyDiscountCode($this.event.discount_code, function (discountCodeId, message) {
                $this.discountMessage.loading = false;
                if (_.isNull(discountCodeId)) {
                    $this.discountMessage.success = '';
                    $this.discountMessage.error = message;
                } else {
                    $this.discountMessage.success = message;
                    $this.discountMessage.error = '';
                    $this.event.discount_code_id = discountCodeId;
                }
            });
        }
    },
    compiled: function () {

    }
});

basicDetailsApp.$nextTick(function () {
    var $eventDiv = $(this.$el);
    /* Bind datepicker to dates */
    $eventDiv.find("input.date").datepicker({
        'format': 'mm/dd/yyyy',
        'autoclose': true,
        'startDate': new Date()
    }).on('changeDate', function (e) {
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
});


VueGoogleMap.loaded.then(function () {
    window.geocoder = new google.maps.Geocoder();
    var locationInput = $("#location_name")[0];
    window.autocomplete = new google.maps.places.Autocomplete(locationInput, {types: ['geocode']});
    window.autocomplete.addListener('place_changed', function () {
        locationInput.dispatchEvent(new Event('input'));
    });

    var intervalID = setInterval(function () {
        try {
            if (!_.isUndefined(basicDetailsApp.$refs.gmap.$mapObject)) {
                clearInterval(intervalID);
                window.map = basicDetailsApp.$refs.gmap.$mapObject;
                basicDetailsApp.recenterMap();
                basicDetailsApp.mapLoaded = true;
            }
        } catch (ignored) {
        }
    }, 100);
});
