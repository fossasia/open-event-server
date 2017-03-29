// Function that initializes a DataTable on .tables inside $(element).
function initDataTable(element) {
    if (!$.fn.DataTable.isDataTable(element + ' .table')) {
        // The table on 'Import' tab has a different number of columns.
        if (element === '#import') {
            return $(element + ' .table').DataTable();
        }

        return $(element + ' .table').DataTable({
            "columnDefs": [
                { "width": "7%", "targets": 0 },
                { "width": "15%", "targets": 1 },
                { "width": "23%", "targets": 2 },
                { "width": "10%", "targets": 3 },
                { "width": "10%", "targets": 4 },
                { "width": "10%", "targets": 6 }
            ]
        });
    }
    return;
}

$(document).ready(function () {
    $('.progress .progress-bar').progressbar({display_text: 'center', use_percentage: false});
});

$('.accordion-link').click(function () {
    $('.accordion-link').removeClass('active');
    $(this).addClass('active');
});

$(document).ready(function () {
    // In case in tab is specified, the `Live` tab is shown by default.
    // Update the hash accordingly.
    if (location.hash === "" || location.hash === "#") {
        location.replace("#!live");
    }

    if (location.hash.substr(0, 2) === "#!") {
        $("a[href='#" + location.hash.substr(2) + "']").tab("show");
        // Initialize the DataTable on the current tab on first load.
        initDataTable('#' + location.hash.substr(2));
    }

    $("a[data-toggle='tab']").on("shown.bs.tab", function (e) {
        var hash = $(e.target).attr("href");
        // Initialize DataTables in a hidden tab only on swicthing to that tab.
        initDataTable(hash);
        if (hash.substr(0, 1) === "#") {
            location.replace("#!" + hash.substr(1));
        }
    });
});

$(".small_tab_list").click(function () {
    $(".small_tab_list").removeClass("active");
    $(this).addClass("active");
    var clicked_link = $(this).attr("value");
    $(".drop_header").text(clicked_link);
});

$('.tabs_small a').click(function () {
    $(this).tab('show');
});
