var tracksSeed = null;
var sessionTypesSeed = null;
var microlocationsSeed = null;
var callForSpeakersSeed = null;
var enabled = false;

if (!_.isUndefined(window.seed)) {
    if (!_.isNull(window.seed.tracks)) {
        tracksSeed = window.seed.tracks;
        enabled = enabled || tracksSeed.length > 0;
    }
    if (!_.isNull(window.seed.sessionTypes)) {
        sessionTypesSeed = window.seed.sessionTypes;
        enabled = enabled || sessionTypesSeed.length > 0;
    }
    if (!_.isNull(window.seed.microlocations)) {
        microlocationsSeed = window.seed.microlocations;
        enabled = enabled || microlocationsSeed.length > 0;
    }
    if (!_.isNull(window.seed.callForSpeakers)) {
        callForSpeakersSeed = window.seed.callForSpeakers;
    }
}

//noinspection JSUnusedGlobalSymbols
var sessionsSpeakersApp = new Vue({
    el: '#event-wizard-sessions-speakers',
    data: {
        tracks: (tracksSeed && tracksSeed.length > 0) ? tracksSeed : [],
        sessionTypes: (sessionTypesSeed && sessionTypesSeed.length > 0) ? sessionTypesSeed : [],
        microlocations: (microlocationsSeed && microlocationsSeed.length > 0) ? microlocationsSeed : [],
        call_for_speakers: callForSpeakersSeed ? callForSpeakersSeed : getCallForSpeakers(),
        sessions_speakers_enabled: enabled,
        custom_forms: {
            session: [],
            speaker: []
        }
    },
    watch: {
        'sessions_speakers_enabled': function (value) {
            if (value) {
                this.tracks = [getNewTrack('Main Track')];
                this.sessionTypes = [getNewSessionType('Talks')];
                this.microlocations = [getNewMicrolocation('Room 1')];
                this.call_for_speakers = getCallForSpeakers();
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
        }
    }
});


sessionsSpeakersApp.$nextTick(function () {
    var $eventDiv = $(this.$el);

    $eventDiv.find('[data-toggle="tooltip"]').tooltip();

    var clipboard = new Clipboard('.btn-copy');
    clipboard.on('success', function () {
        $eventDiv.find(".btn-copy")
            .attr("title", "Copied")
            .attr("data-original-title", "Copied")
            .tooltip('show')
            .attr("title", "Click to copy")
            .attr("data-original-title", "Click to copy");
    });

    $eventDiv.find("input.date").datepicker({
        'format': 'mm/dd/yyyy',
        'autoclose': true,
        'startDate': new Date()
    }).on('changeDate', function () {
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

    $eventDiv.find(".announcement").summernote(summernoteConfig);

    persistData();
});

function persistData() {
    Vue.set(sessionsSpeakersApp.custom_forms, 'session', sessionForm[0]);
    Vue.set(sessionsSpeakersApp.custom_forms, 'speaker', speakerForm[0]);
}
