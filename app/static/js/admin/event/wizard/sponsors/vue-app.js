var sponsorsSeed = null;

if(!_.isUndefined(window.seed) && !_.isNull(window.seed.sponsors)) {
    sponsorsSeed = window.seed.sponsors;
}

//noinspection JSUnusedGlobalSymbols
var sponsorsApp = new Vue({
    el: '#event-wizard-sponsors',
    data: {
        sponsors: (sponsorsSeed && sponsorsSeed.length > 0) ? sponsorsSeed : [],
        event_id: sponsorsSeed ? window.seed.event.id : null,
        sponsors_enabled: !!(sponsorsSeed && sponsorsSeed.length > 0)
    },
    watch: {
        'sponsors_enabled': function (value) {
            if (value) {
                this.sponsors = [_.clone(SPONSOR)];
            } else {
                this.sponsors = [];
            }
            this.$nextTick(function () {
                bindSummerNote(this);
            })
        }
    },
    methods: {
        addSponsor: function () {
            this.sponsors.push(_.clone(SPONSOR));
            this.$nextTick(function () {
                bindSummerNote(this);
            });
        },
        removeSponsor: function (sponsor) {
            var index = this.sponsors.indexOf(sponsor);
            this.sponsors.splice(index, 1);
        }
    }
});

function bindSummerNote($this) {
    var $eventDiv = $($this.$el);
    $eventDiv.find("textarea:not(:hidden)").summernote(summernoteConfig);
}
