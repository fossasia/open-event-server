var $ticketFilterForm = $("#ticket-filter-form");
var base_url = [location.protocol, '//', location.host, location.pathname].join('');

$(".ticket-filter-open").click(function() {
    $ticketFilterForm.show();
    $ticketFilterForm.find("select").val("");
});

function make_request() {
    var from_date = $("#from_date").val();
    var to_date = $("#to_date").val();
    var ticket_name = $("#sel1").val();
    var prop = $ticketFilterForm.css('display');
    var fieldObjs = {};

    if (prop === "none" || ticket_name === null) {
        ticket_name = '';
    }

    if (from_date !== '') {
        fieldObjs['from_date'] = from_date;
    }

    if (to_date !== '') {
        fieldObjs['to_date'] = to_date;
    }

    if (ticket_name !== '') {
        fieldObjs['ticket_name'] = ticket_name;
    }

    var queryString = $.param(fieldObjs, true);
    if(queryString !== '') {
        base_url = base_url + "?" + queryString;
    }
    window.location.replace(base_url);
}

$(".form-filter").click(function() {
    make_request();
});

$("#date-filter-remove").click(function () {
    $dateFilterForm.find("input").val("");
    $dateFilterForm.hide();
    make_request();
});

$("#ticket-filter-remove").click(function () {
    $ticketFilterForm.find("select").val('');
    $ticketFilterForm.hide();
    make_request();
});

$("#all-filters-remove").click(function() {
    $ticketFilterForm.find("select").val("");
    $ticketFilterForm.hide();
    $dateFilterForm.find("input").val("");
    $dateFilterForm.hide();
    make_request();
});
