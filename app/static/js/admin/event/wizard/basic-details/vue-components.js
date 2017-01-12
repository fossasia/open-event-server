Vue.component('ticket', {
    props: ['ticket', 'service_fee'],
    data: function () {
        return {
            show_settings: false
        };
    },
    template: '#ticket-template',
    methods: {
        remove: function () {
            this.$emit('remove');
        }
    },
    mounted: function () {
        this.$nextTick(function () {
            var $ticket = $(this.$el);
            var event = new Event('input');
            /* Bind datepicker to dates */
            $ticket.find("input.date").datepicker().on('changeDate', function () {
                this.dispatchEvent(event);
            });
            $ticket.find("input.time").timepicker({
                'showDuration': true,
                'timeFormat': 'H:i',
                'scrollDefault': 'now'
            }).on('changeTime', function () {
                this.dispatchEvent(event);
            });
            /* iCheck for Ticket description toggle checkbox */
            $ticket.find("input.checkbox.flat").iCheck({
                checkboxClass: 'icheckbox_flat-green',
                radioClass: 'iradio_flat-green'
            });
            $ticket.find(".ticket-tags").selectize({
                plugins: ['remove_button'],
                persist: false,
                createOnBlur: true,
                create: true,
                onChange: function () {
                    $ticket.find(".ticket-tags")[0].dispatchEvent(event);
                }
            });
            /* Enable tooltips */
            $ticket.find(".edit-ticket-button").tooltip();
        });
    }
});

Vue.component('social-link', {
    props: ['socialLink'],
    template: '#social-link-template',
    methods: {
        add: function () {
            this.$emit('add');
        },
        remove: function () {
            this.$emit('remove');
        },
        isValidLinkEntry: function (link) {
            if (link.trim() === '') {
                return true;
            }
            return isLink(link);
        }
    }
});

Vue.use(VueGoogleMap, {
    load: {
        key: 'AIzaSyAHdXg0Y_zk-wCNpslbBqcezLdHniaEwkI',
        v: '3',
        libraries: 'places'
    },
    installComponents: false
});

Vue.component('google-map', VueGoogleMap.Map);
Vue.component('map-marker', VueGoogleMap.Marker);
