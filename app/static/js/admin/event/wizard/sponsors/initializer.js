var sponsorsSeed = null;

if(!_.isUndefined(window.seed) && !_.isNull(window.seed.sponsors)) {
    sponsorsSeed = window.seed.sponsors;
}

function bindSummerNote($this) {
    var $eventDiv = $($this.$el);
    $eventDiv.find("textarea:not(:hidden)").summernote(summernoteConfig);
}
