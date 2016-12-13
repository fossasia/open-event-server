Vue.component('button-bar', {
    template: '#button-bar-template',
    props: ['showPrev', 'state'],
    methods: {
        move: function (e) {
            this.$emit('move', e.target);
        },
        publish: function () {
            this.$emit('publish', e.target);
        },
        unpublish: function () {
            this.$emit('unpublish', e.target);
        }
    }
});
