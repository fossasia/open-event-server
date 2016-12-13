Vue.component('tabs', {
    template: '#tabs-template',
    props: ['step'],
    methods: {
        moveToStep: function (toStep) {
            console.log(toStep);
            this.$emit('move', toStep);
        }
    }
});
