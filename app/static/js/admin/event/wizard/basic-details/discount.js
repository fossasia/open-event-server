var $discountCodeEntry = $("#discount-code-entry");
var $discountCodeFormGroup = $discountCodeEntry.closest('.form-group');
var $discountCodeId = $discountCodeFormGroup.find('input[name=discount_code_id]');
var $helpText = $discountCodeFormGroup.find('.help-text');
var $discountCodeEntryApply = $("#discount-code-entry-apply");


$discountCodeEntryApply.click(function () {
    $discountCodeFormGroup.removeClass('has-error').removeClass('has-success');
    $helpText.removeClass('text-danger').removeClass('text-success').hide();
    $discountCodeId.val("");
    var discountCodeValue = $discountCodeEntry.val().trim();
    if (discountCodeValue != "") {
        $discountCodeEntry.disable();
        $discountCodeEntryApply.html('Verifying <i class="fa fa-spin fa-cog fa-fw"></i>').disable();
        $.post(discountCodeApplyUrl, {discount_code: discountCodeValue})
            .done(function (data) {
                $discountCodeEntry.enable();
                $discountCodeEntryApply.enable().html('Apply Discount');
                $helpText.show();
                if (data.status === 'ok') {
                    $discountCodeFormGroup.addClass('has-success');
                    $discountCodeId.val(data.discount_code.id);
                    var message = data.discount_code.value + "% over a period of " + data.discount_code.max_quantity + " month(s)";
                    $helpText.addClass('text-success').html("<strong>Discount Applied!</strong> " + message);
                } else {
                    $discountCodeFormGroup.addClass('has-error');
                    if (data.hasOwnProperty('message')) {
                        $helpText.addClass('text-danger').text(data.message);
                    } else {
                        $helpText.addClass('text-danger').text("An error occurred while trying to apply the discount code.");
                    }
                }
            });
    }
});

$discountCodeEntry.valueChange(function (value) {
    $discountCodeFormGroup.removeClass('has-error').removeClass('has-success');
    $helpText.removeClass('text-danger').removeClass('text-success').hide();
    $discountCodeEntryApply.enable().html('Apply Discount');
    $discountCodeId.val("");
});
