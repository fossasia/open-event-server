var sponsorsSeed = null;
var sponsorsEnabled = null;
var ticketsSeed = [];

if(!_.isUndefined(window.seed) && !_.isNull(window.seed.sponsors)  && !_.isNull(window.seed.event)) {
    sponsorsSeed = window.seed.sponsors;
    sponsorsEnabled = window.seed.event.sponsors_enabled;
    ticketsSeed = window.seed.event.tickets;
}

function bindSummerNote($this) {
    var $eventDiv = $($this.$el);
    $eventDiv.find("textarea:not(:hidden)").summernote(summernoteConfig);
}
