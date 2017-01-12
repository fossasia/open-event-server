var SOCIAL_LINK = {
    id: null,
    name: '',
    link: ''
};

FACEBOOK_LINK = _.clone(SOCIAL_LINK);
FACEBOOK_LINK.name = 'Facebook';
TWITTER_LINK = _.clone(SOCIAL_LINK);
TWITTER_LINK.name = 'Twitter';

var EVENT = {
    id: null,
    name: '',
    location_name: '',
    show_map: true,
    start_time_date: moment().add(1, 'months').format('MM/DD/YYYY'),
    start_time_time: moment().add(1, 'months').hour(10).minute(0).format('HH:mm'),
    end_time_date: moment().add(1, 'months').format('MM/DD/YYYY'),
    end_time_time: moment().add(1, 'months').hour(17).minute(0).format('HH:mm'),
    timezone: current_timezone,
    description: '',
    background_url: '',
    logo: '',
    has_organizer_info: true,
    organizer_name: '',
    organizer_description: '',
    event_url: '',
    social_links: [FACEBOOK_LINK, TWITTER_LINK],
    ticket_include: true,
    tickets: [],
    ticket_url: '',
    discount_code_id: null,
    discount_code: '',
    payment_country: 'United States',
    payment_currency: 'USD',
    pay_by_paypal: false,
    pay_by_stripe: false,
    pay_by_cheque: false,
    pay_by_bank: false,
    pay_onsite: false,
    privacy: 'public',
    type: '',
    topic: '',
    sub_topic: '',
    state: 'Draft',
    has_code_of_conduct: false,
    code_of_conduct: '',
    copyright: {
        holder: '',
        holder_url: null,
        licence: '',
        licence_url: '',
        logo: '',
        year: 2016
    },
    tax_allow: 0,
    tax: {
        country: '',
        tax_name: '',
        tax_rate: '',
        tax_id: '',
        send_invoice: false,
        registered_company: '',
        address: '',
        city: '',
        state: '',
        zip: '',
        invoice_footer: '',
        tax_include_in_price: 1
    },
    latitude: 0.0,
    longitude: 0.0,
    stripe: {
        linked: false,
        stripe_secret_key: '',
        stripe_refresh_token: '',
        stripe_publishable_key: '',
        stripe_user_id: '',
        stripe_email: ''
    }
};

var TICKET = {
    id: null,
    name: '',
    type: '',
    has_orders: false,
    price: 0,
    quantity: 100,
    description: '',
    description_visibility: false,
    ticket_visibility: false,
    sales_start_date: moment().format('MM/DD/YYYY'),
    sales_start_time: moment().format('HH:mm'),
    sales_end_date: moment().add(10, 'days').format('MM/DD/YYYY'),
    sales_end_time: moment().add(10, 'days').hour(22).minute(0).format('HH:mm'),
    min_order: 1,
    max_order: 10,
    tags_string: '',
    absorb_fees: false
};
