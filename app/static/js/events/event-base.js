var deleteButton = $('#delete-event-button');
var deleteCheck = $('#delete-check');
var eventName = deleteCheck.attr('data-event-name');

deleteButton.addClass('disabled');
deleteCheck.keyup(function() {
     if(deleteCheck.val() === eventName) {
            deleteButton.removeClass('disabled');
     }
     else {
        if(!deleteButton.hasClass('disabled')) {
        	deleteButton.addClass('disabled');
        }
     }
});
