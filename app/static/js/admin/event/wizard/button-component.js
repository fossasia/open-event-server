Vue.component('button-bar', {
    template: '#button-bar-template',
    props: ['state', 'step', 'disable'],
    methods: {
        move: function (direction) {
            this.$emit('move', direction);
        },
        publish: function () {
            this.$emit('publish');
        },
        unpublish: function () {
            this.$emit('unpublish');
        }
    }
});
