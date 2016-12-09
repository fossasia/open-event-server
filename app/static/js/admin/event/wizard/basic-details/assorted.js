$('.time').timepicker({
    'showDuration': true,
    'timeFormat': 'H:i',
    'scrollDefault': 'now'
});

$('.date').datepicker({
    'format': 'mm/dd/yyyy',
    'autoclose': true,
    'startDate': new Date()
});

$(".event-date-picker").datepair({
    'defaultTimeDelta': 3600000
});

$("textarea.event-textarea").summernote(summernoteConfig);

$('select[name=timezone]').selectize({
    create: false,
    sortField: 'text'
});

$(".licence-help").click(function () {
    $("#licence-list").slideToggle();
});


var $topic = $("#topic");
var $subTopic = $('#sub_topic');
$topic.change(function () {
    $subTopic.find('option').remove().end().append('<option value="">Choose..</option>');
    $.each(sub_topics[$(this).val()], function () {
        $subTopic.append($("<option />").val(this).text(this));
    });
});

if ($topic.val() !== "") {
    $subTopic.find('option').remove().end().append('<option value="">Choose..</option>');

    $.each(sub_topics[$topic.val()], function () {
        $subTopic.append($("<option />").val(this).text(this));
    });
    $subTopic.val("{{event.sub_topic}}");
}

var $taxformHolder = $("#tax-form-holder");
$("#taxYes").on("click", function () {
    $taxformHolder.fadeIn();
});
$("#taxNo").on("click", function () {
    $taxformHolder.fadeOut();
});

var $taxinvoiceHolder = $("#tax-invoice-holder");
$("#tax_invoice").change(function () {
    if ($("#tax_invoice").is(":checked"))
        $taxinvoiceHolder.fadeIn();
    else
        $taxinvoiceHolder.fadeOut();
});

$(document).on("click", '.add-social-links', function () {
    var $element = $($(".social-link-holder")[0]).clone();
    $element.find("input").val('').attr("value", "");
    $('.social-links > div').append($element);
});

$(document).on("click", ".remove-social-links", function () {
    if ($('.social-links > div').children().length > 1) {
        $(this).closest(".social-link-holder").remove();
    }
});

function resetFormElement(e) {
    e = $(e);
    e.wrap('<form>').closest('form').get(0).reset();
    e.unwrap();
}

var $cocHolder = $("#coc-holder");
var $cocState = $(".coc-state");

var coc_onOffSwitch = document.getElementById('coc-switch');

coc_onOffSwitch.onchange = function () {
    if (coc_onOffSwitch.checked) {
        $cocHolder.fadeIn();
        $cocState.text("Remove");
    } else {
        $cocHolder.fadeOut();
        $cocState.text("Add");
    }
};

var $organizerHolder = $("#organizer-holder");
var $organizerState = $(".organizer-state");

var organizer_onOffSwitch = document.getElementById('organizer-switch');

organizer_onOffSwitch.onchange = function () {
    if (organizer_onOffSwitch.checked) {
        $organizerHolder.fadeIn();
        $organizerState.text("Remove");
    } else {
        $organizerHolder.fadeOut();
        $organizerState.text("Add");
    }
};

