Vue.component('filter-tag', {
    template: '#filter-tag-template',
    props: ['name', 'value'],
    methods: {
        remove: function () {
            this.$emit('remove');
        }
    }
});
