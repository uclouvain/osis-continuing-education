function openRejectedModal() {
    $('#rejected_reason_modal').modal('show');
    $('#old_predefined_rejected_reason').val($('#id_rejected_reason').val());
    $('#old_other_reason').val($('#id_other_reason').val());

}

function disabledEnabledOtherReasonInputText(){
    if(document.getElementById("id_rejected_reason").value == "Other" || document.getElementById("id_rejected_reason").value == "Autre"){
        document.getElementById("id_other_reason").disabled = false;
    }else{
        document.getElementById("id_other_reason").disabled = true;
        $("#id_other_reason").val('');
    }
}

$('#add_rejected_reason').click(function () {
    $('#form').submit();
})

$("#cancel_rejected_reason").click(function () {
    $('#id_rejected_reason').val($('#old_predefined_rejected_reason').val());
    $('#id_other_reason').val($('#old_other_reason').val());

    if ($('#id_rejected_reason').val() == 'Other' || $('#id_rejected_reason').val() == 'Autre' ){
        $('#id_other_reason').prop('disabled', false);
    }else{
        $('#id_other_reason').prop('disabled', true);
    }

});
