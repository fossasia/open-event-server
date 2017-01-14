$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex) {
        var user_option = $("input[name=show_state]:checked").val();
        var state = data[0].trim() || 'pending';
        if (user_option === "all") {
            return true;
        } else if (user_option === state) {
            return true;
        }
        return false;
    });

var table = $('.with-datatable').DataTable({
    "dom": '<"row"<"toolbar col-md-7"<"pull-left"l>><"col-md-3 pull-right"f>>tip',
    "columnDefs": [
        {"width": "20%", "targets": 1},
        {"width": "5%", "targets": 3}
    ],
    "scrollX": true
});

$("div.toolbar").prepend($("#toolbar-holder").html());

$("input[name=show_state]").change(function () {
    table.draw();
});

table.on('draw', function () {
    $('[data-toggle="tooltip"]').tooltip();
});
$('#mailModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var sessionid = button.data('sessionid'); // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var emailtype = button.data('typeofmail');
    var sessiontitle = button.data('sessiontitle');
    var modal = $(this);
    if (emailtype === "accept") {
        modal.find('.subject').val("Session " + sessiontitle + " has been accepted");
        modal.find('.message').val("Hello,The session " + sessiontitle + " has been " + emailtype + "ed by the organizer.  Visit this link to view the session: http://localhost:8001/events/4/sessions/1/");
        modal.find('.form-horizontal').attr('action', sessionid + '/accept');
    } else {
        modal.find('.subject').val("Session " + sessiontitle + " has been rejected");
        modal.find('.message').val("Hello,The session " + sessiontitle + " has been " + emailtype + "ed by the organizer.  Visit this link to view the session: http://localhost:8001/events/4/sessions/1/");
        modal.find('.form-horizontal').attr('action' , sessionid + '/reject');
    }

});
