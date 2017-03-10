var $dateFilterForm = $("#date-filter-form");
var $filterControlBtn = $("#filter-control-btn");
var $discountFilterForm = $("#discount-filter-form");

$dateFilterForm.find(".date").datepicker({
    'format': 'dd/mm/yyyy',
    'autoclose': true
});

$dateFilterForm.find(".time").timepicker({
    'showDuration': true,
    'timeFormat': 'g:ia'
});

var date = new Datepair($dateFilterForm[0], {
    'defaultDateDelta': 7
});

$(".date-filter-open").click(function () {
    $dateFilterForm.show();
    $dateFilterForm.find("input").val("");
});

$(".filter-remove").click(function () {
    $dateFilterForm.find("input").val("");
    $dateFilterForm.hide();

    $discountFilterForm.find("input").val("");
    $discountFilterForm.hide();

    $dateFilterForm.submit();
    $filterControlBtn.show();
});

$(".discount-filter-open").click(function () {
    $discountFilterForm.show();
    $discountFilterForm.find("input").val("");
});
