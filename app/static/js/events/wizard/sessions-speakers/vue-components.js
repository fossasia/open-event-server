Vue.component('session-track', {
    props: ['track'],
    template: '#track-template',
    methods: {
        remove: function () {
            this.$emit('remove');
        },
        add: function () {
            this.$emit('add');
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            var $div = $(this.$el);
            $div.find('.colorpicker-component').colorpicker().on('changeColor', function () {
                $div.find('input.color-picker-input')[0].dispatchEvent(new Event('input'));
            });
        });
    }
});

Vue.component('microlocation', {
    props: ['microlocation'],
    template: '#microlocation-template',
    methods: {
        remove: function () {
            this.$emit('remove');
        },
        add: function () {
            this.$emit('add');
        }
    }
});

Vue.component('session-type', {
    props: ['sessionType'],
    template: '#session-type-template',
    methods: {
        remove: function () {
            this.$emit('remove');
        },
        add: function () {
            this.$emit('add');
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            var $div = $(this.$el);
            $div.find(".session-length").timepicker({
                'timeFormat': 'H:i'
            }).on('changeTime', function () {
                this.dispatchEvent(new Event('input'));
            });
        });
    }
});
