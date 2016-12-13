Vue.component('tabs', {
    template: '#tabs-template',
    props: ['step', 'disable'],
    methods: {
        moveToStep: function (toStep) {
            this.$emit('move', toStep);
        }
    }
});
