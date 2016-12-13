//noinspection JSUnusedGlobalSymbols
var app = new Vue({
    el: '#wizard',
    data: {
        step: step,
        event: EVENT,
        included_settings: included_settings,
        addressShown: false,
        mapLoaded: false,
        discountMessage: {
            success: '',
            error: '',
            loading: false
        },
        sponsors: (sponsorsSeed && sponsorsSeed.length > 0) ? sponsorsSeed : [],
        sponsors_enabled: (sponsorsSeed && sponsorsSeed.length > 0),
        tracks: (tracksSeed && tracksSeed.length > 0) ? tracksSeed : [],
        sessionTypes: (sessionTypesSeed && sessionTypesSeed.length > 0) ? sessionTypesSeed : [],
        microlocations: (microlocationsSeed && microlocationsSeed.length > 0) ? microlocationsSeed : [],
        call_for_speakers: callForSpeakersSeed ? callForSpeakersSeed : getCallForSpeakers(EVENT),
        sessions_speakers_enabled: enabled,
        custom_forms: {
            session: [],
            speaker: []
        }
    },
    computed: {
        _: function () {
            return _;
        },
        subTopics: function () {
            if (_.isNull(this.event.topic)) {
                return [];
            }
            return sub_topics[this.event.topic];
        },
        location: function () {
            return {
                lat: this.event.latitude,
                lng: this.event.longitude
            };
        },
        zoom: function () {
            return this.event.latitude === 0.0 && this.event.longitude === 0.0 ? 1 : 15;
        }
    },
    watch: {
        'event.topic': function () {
            this.event.sub_topic = '';
        },
        'event.ticket_include': function () {
            this.event.tickets = [];
            this.ticket_url = '';
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
                if (val.trim() !== "") {
                    $this.addressShown = true;
                }
                $this.event.latitude = lat;
                $this.event.longitude = lng;
            });
        },
        'event.discount_code': function () {
            this.discountMessage.success = '';
            this.discountMessage.error = '';
        },
        'sponsors_enabled': function (value) {
            if (value) {
                this.sponsors = [_.clone(SPONSOR)];
            } else {
                this.sponsors = [];
            }
            this.$nextTick(function () {
                bindSummerNote(this);
            });
        },
        'sponsors': function (sponsors) {
            if (sponsors.length <= 0) {
                this.sponsors_enabled = false;
            }
        },
        'sessions_speakers_enabled': function (value) {
            if (value) {
                this.tracks = [getNewTrack('Main Track')];
                this.sessionTypes = [getNewSessionType('Talks')];
                this.microlocations = [getNewMicrolocation('Room 1')];
                this.call_for_speakers = getCallForSpeakers(this.event);
            } else {
                this.tracks = [];
                this.sessionTypes = [];
                this.microlocations = [];
            }
        },
        'tracks': function (value) {
            if (value.length <= 0) {
                this.tracks = [getNewTrack('Main Track')];
            }
        },
        'microlocations': function (value) {
            if (value.length <= 0) {
                this.microlocations = [getNewMicrolocation('Room 1')];
            }
        },
        'sessionTypes': function (value) {
            if (value.length <= 0) {
                this.sessionTypes = [getNewSessionType('Talks')];
            }
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
            _.each(window.componentForm, function (component) {
                locationName += $('#' + component).get(0).value + " ";
            });
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
        },
        addSponsor: function () {
            this.sponsors.push(_.clone(SPONSOR));
            this.$nextTick(function () {
                bindSummerNote(this);
            });
        },
        removeSponsor: function (sponsor) {
            var index = this.sponsors.indexOf(sponsor);
            this.sponsors.splice(index, 1);
        },
        addTrack: function () {
            this.tracks.push(getNewTrack());
        },
        removeTrack: function (track) {
            var index = this.tracks.indexOf(track);
            this.tracks.splice(index, 1);
        },
        addMicrolocation: function () {
            this.microlocations.push(getNewTrack());
        },
        removeMicrolocation: function (microlocation) {
            var index = this.microlocations.indexOf(microlocation);
            this.microlocations.splice(index, 1);
        },
        addSessionType: function () {
            this.sessionTypes.push(getNewTrack());
        },
        removeSessionType: function (sessionType) {
            var index = this.sessionTypes.indexOf(sessionType);
            this.sessionTypes.splice(index, 1);
        },
        moveToStep: function (step) {
            console.log(step);
            this.step = step;
            history.replaceState(null, '', "./" + step);
        }

    },
    compiled: function () {

    }
});

app.$nextTick(function () {
    var $eventDiv = $(this.$el);
    basicDetailsInit($eventDiv);
    sessionSpeakersInit($eventDiv);
});


