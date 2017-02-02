$(document).ready(function () {
    function toggleChevron(e) {
        $(e.target)
            .prev('.panel-heading')
            .find("i.indicator")
            .toggleClass('fa-caret-down fa-caret-right');
    }

    $('#accordion').on('hidden.bs.collapse', toggleChevron).on('shown.bs.collapse', toggleChevron);
});
