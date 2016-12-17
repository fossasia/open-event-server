Vue.component('event-box', {
    template: '#event-box-template',
    props: ['event'],
    methods: {
        share: function (toStep) {
            this.$emit('share');
        },
        eventTagFilter: function (name, value) {
            this.$emit('filter', name, value);
        }
    }
});
