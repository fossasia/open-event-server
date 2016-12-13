Vue.component('save', {
    template: '#button-bar-template',
    methods: {
        add: function (event) {
            this.$emit('add');
        },
        remove: function (event) {
            this.$emit('remove');
        }
    }
});
