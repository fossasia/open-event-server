Vue.component('save', {
    template: '#button-bar-template',
    methods: {
        add: function () {
            this.$emit('add');
        },
        remove: function () {
            this.$emit('remove');
        }
    }
});
