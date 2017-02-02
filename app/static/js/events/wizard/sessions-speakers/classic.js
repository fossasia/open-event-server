window.sessionForm = [{}];
window.speakerForm = [{}];

Array.prototype.setIncluded = function (field, state) {
    this[0][field].include = state ? 1 : 0;
};

Array.prototype.setRequired = function (field, state) {
    this[0][field].require = state ? 1 : 0;
};

function includeClick(button) {
    var $row = $(button).closest("tr");
    var $button = $(button);
    var $requireSwitch = $row.find(".require-switch");
    if (!button.checked) {
        if ($requireSwitch[0].checked) {
            $requireSwitch.click();
        }
    }

    if ($button.data('group') === 'session') {
        sessionForm.setIncluded($row.data('identifier'), button.checked);
    } else if ($button.data('group') === 'speaker') {
        speakerForm.setIncluded($row.data('identifier'), button.checked);
    }
    persistData();
}

function requireClick(button) {
    var $row = $(button).closest("tr");
    var $button = $(button);
    var $includeSwitch = $row.find(".include-switch");
    if (!$includeSwitch[0].checked) {
        $includeSwitch.click();
    }
    if ($button.data('group') === 'session') {
        sessionForm.setRequired($row.data('identifier'), button.checked);
    } else if ($button.data('group') === 'speaker') {
        speakerForm.setRequired($row.data('identifier'), button.checked);
    }
    persistData();
}

$(function () {
    $.each($(".session-options-table").find('tr[data-identifier]'), function (key, row) {
        var $row = $(row);
        sessionForm[0][$row.data('identifier')] = {
            include: $row.find('.include-switch')[0].checked ? 1 : 0,
            require: $row.find('.require-switch')[0].checked ? 1 : 0
        };
    });

    $.each($(".speaker-options-table").find('tr[data-identifier]'), function (key, row) {
        var $row = $(row);
        speakerForm[0][$row.data('identifier')] = {
            include: $row.find('.include-switch')[0].checked ? 1 : 0,
            require: $row.find('.require-switch')[0].checked ? 1 : 0
        };
    });

    $('[data-toggle="tooltip"]').tooltip();
});
