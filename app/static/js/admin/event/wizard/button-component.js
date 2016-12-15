Vue.component('button-bar', {
    template: '#button-bar-template',
    props: ['state', 'step', 'disable', 'locationName'],
    methods: {
        move: function (direction) {
            this.$emit('move', direction);
        },
        publish: function () {
            this.$emit('publish');
        },
        unpublish: function () {
            this.$emit('unpublish');
        },
        saveAsDraft: function () {
            this.$emit('save');
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            var $div = $(this.$el);
            $div.find('[data-toggle=tooltip]').tooltip();
        });
    }
});
