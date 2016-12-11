Vue.config.silent = false;

Vue.component('ticket', {
    props: ['ticket'],
    data: function () {
        return {
            show_settings: false
        }
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
            $ticket.find("input.date").datepicker().on('changeDate', function (e) {
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
        })
    }
});

Vue.component('social-link', {
    props: ['socialLink'],
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

var app = new Vue({
    el: '#event-wizard-step-one',
    components: {
        FileUpload: VueUploadComponent
    },
    data: {
        event: EVENT,
        included_items: included_settings
    },
    computed: {
        _: function () {
            return _;
        },
        subTopics: function () {
            if (_.isNull(this.event.topic)) {
                return []
            }
            return sub_topics[this.event.topic]
        }
    },
    watch: {
        'event.topic': function (val) {
            this.event.sub_topic = ''
        },
        'event.ticket_include': function (val) {
            this.event.tickets = []
        }
    },
    methods: {
        addSocialLink: function () {
            this.event.social_links.push(_.clone(SOCIAL_LINK));
        },
        removeSocialLink: function (socialLink) {
            var index = this.event.social_links.indexOf(socialLink);
            this.event.social_links.splice(index, 1);
        },
        removeTicket: function (ticket) {
            var index = this.event.tickets.indexOf(ticket);
            this.event.tickets.splice(index, 1);
        },
        addTicket: function (ticketType) {
            var ticket = _.cloneDeep(TICKET);
            ticket.type = ticketType;
            this.event.tickets.push(ticket)
        }
    },
    compiled: function () {
        this.upload = this.$refs.upload;
        this.files = this.$refs.upload.files;
    },
    events: {
        addFileUpload: function (file, component) {
            console.log('addFileUpload');
            if (this.auto) {
                component.active = true;
            }
        },
        fileUploadProgress: function (file, component) {
            console.log('fileUploadProgress ' + file.progress);
        },
        afterFileUpload: function (file, component) {
            console.log('afterFileUpload');
        },
        beforeFileUpload: function (file, component) {
            console.log('beforeFileUpload');
        }
    }
});

app.$nextTick(function () {
    var $eventDiv = $(this.$el);
    var event = new Event('input');
    /* Bind datepicker to dates */
    $eventDiv.find("input.date").datepicker({
        'format': 'mm/dd/yyyy',
        'autoclose': true,
        'startDate': new Date()
    }).on('changeDate', function (e) {
        this.dispatchEvent(event);
    });
    $eventDiv.find("input.time").timepicker({
        'showDuration': true,
        'timeFormat': 'H:i',
        'scrollDefault': 'now'
    }).on('changeTime', function () {
        this.dispatchEvent(event);
    });
    $eventDiv.find("textarea.event-textarea").summernote(summernoteConfig);
    $eventDiv.find(".event-date-picker").datepair({
        'defaultTimeDelta': 3600000
    });
    $eventDiv.find(".licence-help").click(function () {
        $("#licence-list").slideToggle();
    });
});

