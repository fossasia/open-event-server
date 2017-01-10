var steps = ['', 'sponsors', 'sessions-tracks-rooms'];

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
        },
        networkRequestRunning: false,
        disableMove: false
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
        },
        invalidDateRange: function () {
            if(this.event.end_time_date.trim().length <= 0
                || this.event.end_time_time.trim().length <= 0
                || this.event.start_time_date.trim().length <= 0
                || this.event.start_time_time.trim().length <= 0) {
                return false;
            }
            var format = 'MM/DD/YYYY HH:mm';
            var start = moment(this.event.start_time_date.trim() + " " + this.event.start_time_time.trim(), format);
            var end = moment(this.event.end_time_date.trim() + " " + this.event.end_time_time.trim(), format);
            return end.isBefore(start);
        }
    },
    watch: {
        'event.topic': function () {
            this.event.sub_topic = '';
        },
        'event.ticket_include': function () {
            this.event.tickets = [];
            this.ticket_url = '';
            save(this.step);
        },
        'addressShown': function (val) {
            if (val) {
                var $this = this;
                setTimeout(function () {
                    $this.recenterMap();
                }, 500);
            }
        },
        'invalidDateRange': function (value) {
            this.disableMove = this.disableMove ? this.disableMove : value;
        },
        'event.name': function () {
            this.disableMove = shouldDisableMove(this);
        },
        'event.start_time_time': function () {
            this.disableMove = shouldDisableMove(this);
        },
        'event.start_time_date': function () {
            this.disableMove = shouldDisableMove(this);
        },
        'event.end_time_time': function () {
            this.disableMove = shouldDisableMove(this);
        },
        'event.end_time_date': function () {
            this.disableMove = shouldDisableMove(this);
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
            save(this.step);
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
            save(this.step);
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
        },
        'step': function (step) {
            history.replaceState(null, '', "./" + step);
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
        removeTicket: function (ticket, force) {
            if (_.isUndefined(force)) {
                force = false;
            }
            if (force || confirm("Are you sure you want to remove this ticket ?")) {
                var index = this.event.tickets.indexOf(ticket);
                this.event.tickets.splice(index, 1);
            }
        },
        addTicket: function (ticketType) {
            var ticket = _.cloneDeep(TICKET);
            ticket.sales_start_date = moment().tz(this.event.timezone).format('MM/DD/YYYY');
            ticket.sales_start_time = moment().tz(this.event.timezone).format('HH:mm');
            ticket.sales_end_date = moment().tz(this.event.timezone).add(10, 'days').format('MM/DD/YYYY'),
            ticket.sales_end_time = moment().tz(this.event.timezone).add(10, 'days').hour(22).minute(0).format('HH:mm'),
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
            _.each(window.componentForm, function (value, key) {
                locationName += $('#' + key).get(0).value + " ";
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
            this.microlocations.push(getNewMicrolocation());
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
            var $this = this;
            if (_.isNull(this.event.id)) {
                showLoading("Saving the event");
            } else {
                showLoading("Saving changes");
            }
            save($this.step, this.event.state, function () {
                $this.step = step;
            });

        },
        move: function (direction) {
            var $this = this;
            if (_.isNull(this.event.id)) {
                showLoading("Saving the event");
            } else {
                showLoading("Saving changes");
            }
            save(this.step, this.event.state, function () {
                var index = _.indexOf(steps, $this.step);
                index = direction === 'forward' ? index + 1 : index - 1;
                if (index < steps.length && index >= 0) {
                    $this.step = steps[index];
                } else {
                    location.href = "/events/" + $this.event.id + "/";
                }
            });
        },
        publish: function () {
            var $this = this;
            showLoading("Publishing the event");
            save('all', 'Published', function () {
                $this.event.state = 'Published';
                location.href = "/events/" + $this.event.id + "/";
            });
        },
        unpublish: function () {
            var $this = this;
            showLoading("Un-publishing the event");
            save('all', 'Draft', function () {
                $this.event.state = 'Draft';
            });
        },
        saveAsDraft: function () {
            var $this = this;
            showLoading("Saving the event");
            save('all', 'Draft', function () {
                $this.event.state = 'Draft';
                location.href = "/events/" + $this.event.id + "/";
            });
        },
        isValidLinkEntry: function (link) {
            if(link.trim() === '') {
                return true;
            }
            return isLink(link);
        }
    },
    compiled: function () {

    }
});

app.$nextTick(function () {
    var $eventDiv = $(this.$el);
    this.disableMove = shouldDisableMove(this);
    basicDetailsInit($eventDiv);
    sessionSpeakersInit($eventDiv);
    bindSummerNote(this);
});

function shouldDisableMove($this) {
    return (
        $this.event.name.trim() === '' ||
        $this.event.start_time_time.trim() === '' ||
        $this.event.start_time_date.trim() === '' ||
        $this.event.end_time_time.trim() ==='' ||
        $this.event.end_time_date.trim() === ''
    );
}

function showLoading(text) {
    if (_.isUndefined(text)) {
        text = "Saving";
    }
    createHtmlSnackbar("<i class='fa fa-circle-o-notch fa-lg fa-spin fa-fw'></i>" + text + ' ...', '  ', null, 60000);
}

function save(stepToSave, state, callback) {

    if(shouldDisableMove(app)) {
        return;
    }

    stepToSave = stepToSave === '' ? 'event' : stepToSave;

    cleanData();

    if(_.isUndefined(state)) {
        state = app.event.state;
    }

    var eventsData = {
        event: app.event,
        state: state,
        event_id: app.event.id
    };

    var sponsorsData = {
        event_id: app.event.id,
        sponsors_enabled: app.sponsors_enabled,
        sponsors: app.sponsors,
        state: state
    };

    var sessionsSpeakersData = {
        event_id: app.event.id,
        tracks: app.tracks,
        microlocations: app.microlocations,
        session_types: app.sessionTypes,
        call_for_speakers: app.call_for_speakers,
        sessions_speakers_enabled: app.sessions_speakers_enabled,
        custom_forms: app.custom_forms,
        state: state
    };

    /* Commented out for now until better condition is found
    if (!_.isUndefined(app.event.id) && !_.isNull(app.event.id) && _.isNumber(app.event.id) && !_.isUndefined(callback)) {
        callback();
        callback = null;
    }*/

    switch (stepToSave) {
        case 'event':
            makePost(stepToSave, eventsData, callback);
            break;
        case 'sponsors':
            makePost(stepToSave, sponsorsData, callback);
            break;
        case 'sessions-tracks-rooms':
            makePost(stepToSave, sessionsSpeakersData, callback);
            break;
        case 'all':
            var data = {
                sponsors: sponsorsData,
                session_speakers: sessionsSpeakersData,
                event: eventsData,
                event_id: app.event.id
            };
            makePost('all', data, callback);
            break;
        default:
            /* Commented out for now until better condition is found
            if (!_.isUndefined(callback) && !_.isNull(callback)) {
                callback();
            }*/
    }
}

function cleanData() {
    _.each(app.event.tickets, function (ticket) {
        if (!_.isUndefined(ticket) && !_.isNull(ticket)) {
            if (!ticket.name || ticket.name.trim() === '') {
                app.removeTicket(ticket, true);
            }
        }
    });

    _.each(app.event.social_links, function (social_link) {
        if (!_.isUndefined(social_link) && !_.isNull(social_link)) {
            if (social_link.name.trim() === '' || social_link.link.trim() === '' || !isLink(social_link.link)) {
                app.removeSocialLink(social_link);
            }
        }
    });

    _.each(app.sponsors, function (sponsor) {
        if (!_.isUndefined(sponsor) && !_.isNull(sponsor)) {
            if (sponsor.name.trim() === '') {
                app.removeSponsor(sponsor);
            }
            if (sponsor.url.trim() !== '' && !isLink(sponsor.url)) {
                sponsor.url = '';
            }
        }
    });

    _.each(app.tracks, function (track) {
        if (!_.isUndefined(track) && !_.isNull(track)) {
            if (track.name.trim() === '' || track.color.trim() === '') {
                app.removeTrack(track);
            }
        }
    });

    _.each(app.sessionTypes, function (sessionType) {
        if (!_.isUndefined(sessionType) && !_.isNull(sessionType)) {
            if (sessionType.name.trim() === '') {
                app.removeSessionType(sessionType);
            }
        }
    });

    _.each(app.microlocations, function (microlocation) {
        if (!_.isUndefined(microlocation) && !_.isNull(microlocation)) {
            if (microlocation.name.trim() === '') {
                app.removeMicrolocation(microlocation);
            }
        }
    });
}


function makePost(stepToSave, data, callback) {
    app.networkRequestRunning = true;
    $.ajax({
        type: 'POST',
        url: '/events/save/' + stepToSave + '/',
        data: JSON.stringify(data),
        success: function (response) {
            if (response && response.hasOwnProperty('event_id')) {
                createSnackbar("The changes have been saved successfully.");

                if (_.isNull(app.event.id)) {
                    app.event.id = response.event_id;
                }

                if (_.includes(location.pathname, 'create')) {
                    history.replaceState(null, '', location.pathname.replace('create', response.event_id + '/edit'));
                    $("#page-title").text('Edit Event');
                    document.title =  'Edit Event - ' + $("meta[name=app-name]").attr('content');
                }
                if (!_.isUndefined(callback) && !_.isNull(callback)) {
                    callback();
                }
            } else {
                createSnackbar("An error occurred while saving. Please try again later ...");
            }
        },
        error: function () {
            createSnackbar("An error occurred while saving. Please try again later ...");
        },
        complete: function () {
            app.networkRequestRunning = false;
        },
        contentType: "application/json",
        dataType: 'json'
    });
}
