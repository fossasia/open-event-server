var $ticketsystemHolder = $("#ticket-system-holder");
var $ticketURLHolder = $("#ticket-url-holder");
var $ticketState = $(".ticket-state");
var $ticketsHolder = $form.find(".tickets-holder");
var $paymentSystemHolder = $form.find("#payment-system-holder");
var ticket_onOffSwitch = document.getElementById('ticket-switch');

if (ticket_onOffSwitch != null) {
    ticket_onOffSwitch.onchange = function () {
        if (ticket_onOffSwitch.checked) {
            $ticketsystemHolder.fadeIn();
            $ticketURLHolder.fadeOut();
            $ticketState.text("Add Ticket URL");
        } else {
            $ticketsystemHolder.fadeOut();
            $ticketURLHolder.fadeIn();
            $ticketState.text("Use Ticketing System");
        }
    };
}


$form.find("select#ticket-type").on("change", function () {
    var type = $form.find("option:selected", this).val();
    var ticketTypePrice = $form.find("#ticket-type-price");

    if (type == "free") {
        ticketTypePrice.html("<div class='form-control'>Free</div>");
    } else if (type == "donation") {
        ticketTypePrice.html("<div class='form-control'>Donation</div>");
    } else if (type == "paid") {
        ticketTypePrice.html("<input type='number' class='form-control' placeholder='Set your ticket price' name='ticket_price' required>");
    }
});

var ticketsCount = 1;

$form.find(document).ready(function () {
    $form.find("#event-wizard-form").find(".ticket-tags").selectize({
        plugins: ['remove_button'],
        persist: false,
        createOnBlur: true,
        create: true
    });
});

function addTicket(type) {
    /* Clone ticket from template */
    var $tmpl = $form.find("#ticket-template").clone().children("div");
    var $ticket = $form.find($tmpl[0]).attr("id", "ticket_" + String(ticketsCount));
    var $ticketMore = $form.find($tmpl[1]).attr("id", "ticket-more_" + String(ticketsCount));

    /* Bind datepicker to dates */
    $ticketMore.find("input.date").datepicker();
    $ticketMore.find("input.time").timepicker({
        'showDuration': true,
        'timeFormat': 'H:i',
        'scrollDefault': 'now'
    });

    /* iCheck for Ticket description toggle checkbox */
    $ticketMore.find("input.checkbox.flat").iCheck({
        checkboxClass: 'icheckbox_flat-green',
        radioClass: 'iradio_flat-green'
    });

    $ticketMore.find(".ticket-tags").selectize({
        plugins: ['remove_button'],
        persist: false,
        createOnBlur: true,
        create: true
    });

    /* Bind events to Edit and Remove buttons */
    var $ticketEdit = $ticket.find(".edit-ticket-button");
    $ticketEdit.tooltip();
    $ticketEdit.on("click", function () {
        $ticketMore.slideToggle("slow");
    });
    var $ticketRemove = $ticket.find(".remove-ticket-button");
    $ticketRemove.tooltip();
    $ticketRemove.on("click", function () {
        var confirmRemove = confirm("Are you sure you want to remove the Ticket?");
        if (confirmRemove) {
            if (type == 'paid' || type == 'donation') {
                paid_tickets = paid_tickets - 1;
                if (paid_tickets == 0) {
                    $paymentSystemHolder.fadeOut();
                }
            }
            $ticket.remove();
            $ticketMore.remove();
        }
    });

    /* Set Ticket Type field */
    $ticket.find("input[name='tickets[type]']").val(type);

    /* Set Ticket Price field */
    var html = null;
    if (type === "free") {
        html = '<input type="text" name="tickets[price]" class="form-control" value="Free" readonly>';
    } else if (type === "paid") {
        html = '<input type="number" min="0" name="tickets[price]" class="form-control"  placeholder="Price" value="">';
    } else if (type === "donation") {
        html = '<input type="text" name="tickets[price]" class="form-control" value="Donation" readonly>';
    }
    $form.find($ticket.children()[1]).html(html);

    $ticketMore.find('.ticket-sales.date.end').val($form.find("input[name=end_date]").val());
    $ticketMore.find('.ticket-sales.time.end').val($form.find("input[name=end_time]").val());
    /* Append ticket to table */
    $ticket.hide();
    $ticketMore.hide();
    $ticketsHolder.append($ticket, $ticketMore);
    $ticket.slideToggle();

    /* Set name attribute for all Ticket Description Toggle checkboxes */
    $form.find("input[name*='tickets_description_toggle_']").each(function (i, el) {
        $form.find(el).attr("name", "tickets_description_toggle_" + String(i));
    });
    /* Set name attribute for all Ticket Stop Sales checkboxes */
    $form.find("input[name*='tickets_hide_']").each(function (i, el) {
        $form.find(el).attr("name", "tickets_hide_" + String(i));
    });

    ticketsCount += 1;
}

$form.find(".edit-ticket-button").click(function () {
    var $ticket = $form.find(this).parent().parent().parent();
    var $ticketMore = $ticket.next();
    $ticketMore.slideToggle("slow");
});

$form.find(".remove-ticket-button").click(function () {
    var confirmRemove = confirm("Are you sure you want to remove the Ticket?");
    if (confirmRemove) {
        var $ticket = $form.find(this).parent().parent().parent();
        var $ticketMore = $ticket.next();
        $ticket.remove();
        $ticketMore.remove();
    }
});

$form.find(".add-free-ticket").click(function () {
    addTicket("free");
});

$form.find(".add-paid-ticket").click(function () {
    if (paid_tickets == 0) {
        $paymentSystemHolder.fadeIn();
    }
    paid_tickets += 1;
    addTicket("paid");
});

$form.find(".add-donation-ticket").click(function () {
    if (paid_tickets == 0) {
        $paymentSystemHolder.fadeIn();
    }
    paid_tickets += 1;
    addTicket("donation");
});
