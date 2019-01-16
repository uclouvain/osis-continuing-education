function openRejectedModal() {
    $('#rejected_reason_modal').modal('show');
    $('#old_predefined_rejected_reason').val($('#id_rejected_reason').val());
    $('#old_other_reason').val($('#id_other_reason').val());

}

function disabledEnabledOtherReasonInputText(){
    if(other_selected()){
        document.getElementById("id_other_reason").disabled = false;
    }else{
        document.getElementById("id_other_reason").disabled = true;
        $("#id_other_reason").val('');
        clear_other_reason_error();
    }
}

function other_selected(){
    let selected_element = document.getElementById("id_rejected_reason").value;
    return selected_element === "Other" || selected_element === "Autre";
}

function clear_other_reason_error(){
    $('#id_other_reason').parent().removeClass("has-error");
}

$('#add_rejected_reason').click(function (e) {
    clear_other_reason_error();
    if(!$('#id_other_reason').val() && other_selected()){
        $('#id_other_reason').parent().addClass("has-error");
    } else {
        $('#form').submit();
        $("#rejected_reason_modal").modal('hide');
    }
});

$("#cancel_rejected_reason").click(function () {
    clear_other_reason_error();
    $('#id_rejected_reason').val($('#old_predefined_rejected_reason').val());
    $('#id_other_reason').val($('#old_other_reason').val());

    if (other_selected()){
        $('#id_other_reason').prop('disabled', false);
    }else{
        $('#id_other_reason').prop('disabled', true);
    }

});