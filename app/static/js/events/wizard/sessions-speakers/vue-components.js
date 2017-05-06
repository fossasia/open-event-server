Vue.component('session-track', {
    props: ['track'],
    template: '#track-template',
    watch: {
        'track.color': function(value) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(value);
            if(result) {
                var a = 1 - (0.299 * parseInt(result[1], 16) + 0.587 * parseInt(result[2], 16) + 0.114 * parseInt(result[3], 16))/255;
                this.track.font_color = (a < 0.5) ? '#000000' : '#ffffff';
            }
        }
    },
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
