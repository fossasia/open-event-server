Vue.component('save', {
    template: '#social-link-template',
    methods: {
        add: function (event) {
            this.$emit('add');
        },
        remove: function (event) {
            this.$emit('remove');
        }
    }
});
