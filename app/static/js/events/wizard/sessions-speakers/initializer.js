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

function sessionSpeakersInit($eventDiv) {

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

}
function persistData() {
    Vue.set(app.custom_forms, 'session', sessionForm[0]);
    Vue.set(app.custom_forms, 'speaker', speakerForm[0]);
}
