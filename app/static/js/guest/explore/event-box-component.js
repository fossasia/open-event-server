Vue.component('event-box', {
    template: '#event-box-template',
    props: ['event'],
    data: function () {
        return {
            fallbackImage: ''
        };
    },
    methods: {
        share: function () {
            this.$emit('share');
        },
        eventTagFilter: function (name, value) {
            this.$emit('filter', name, value);
        },
        imageNotFound: function () {
            this.fallbackImage = '/static/img/sativa.png';
        }
    },
    computed: {
        startTimeFormatted: function () {
            return moment(this.event.start_time).format('ddd, MMM DD HH:mm A');
        },
        locationName: function () {
            if (this.event.location_name && _.isString(this.event.location_name)) {
                return this.event.location_name.split(",")[0];
            } else {
                return "";
            }
        },
        backgroundImage: function () {

            if(!_.isNull(this.fallbackImage) && this.fallbackImage.length > 5) {
                return this.fallbackImage;
            }

            if(!isImageInvalid(this.event.thumbnail)) {
                return this.event.thumbnail;
            }
            if(!isImageInvalid(this.event.thumbnail)) {
                return this.event.thumbnail;
            }

            var placeholder;
            if(!_.isNull(this.event.sub_topic) && !_.isEmpty(this.event.sub_topic.trim) && this.event.sub_topic.trim().toLowerCase() != 'other'  && this.event.sub_topic.trim().toLowerCase() != 'others') {
                placeholder = _.get(window.placeholders, this.event.sub_topic, 'sativa.png');
            } else {
                placeholder = _.get(window.placeholders, this.event.topic, 'sativa.png');
            }

            if(placeholder == 'sativa.png' || _.isEmpty(placeholder.trim())) {
                return '/static/img/sativa.png';
            } else {
                return '/static/placeholders/' + placeholder;
            }

        }
    }
});
