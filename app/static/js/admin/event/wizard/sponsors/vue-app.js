//noinspection JSUnusedGlobalSymbols
var app = new Vue({
    el: '#event-wizard-sponsors',
    data: {
        sponsors: [],
        event_id: null,
        sponsors_enabled: false
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
