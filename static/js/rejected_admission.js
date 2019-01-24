function openRejectedModal() {
    $('#rejected_reason_modal').modal('show');
    $('#old_predefined_rejected_reason').val($('#id_rejected-rejected_reason').val());
    $('#old_other_reason').val($('#id_rejected-other_reason').val());

}

function disabledEnabledOtherReasonInputText2(){
    if(otherSelected()){
        alert('in otherselected in disabledEnabledOtherReasonInputText');
        document.getElementById("id_rejected-other_reason").disabled = false;
    }else{
        alert('in else in disabledEnabledOtherReasonInputText');
        document.getElementById("id_rejected-other_reason").disabled = true;
        $("#id_rejected-other_reason").val('');
        clearOtherReasonError();
    }
}

function otherSelected(){
    let selected_element = document.getElementById("id_rejected-rejected_reason").value;
    return selected_element === "Other" || selected_element === "Autre";
}

function clearOtherReasonError(){
    $('#id_rejected-other_reason').parent().removeClass("has-error");
}

$('#add_rejected_reason').click(function (e) {
    clearOtherReasonError();
    if(!$('#id_rejected-other_reason').val() && otherSelected()){
        $('#id_rejected-other_reason').parent().addClass("has-error");
    } else {
        $('#form').submit();
        $("#rejected_reason_modal").modal('hide');
    }
});

$("#cancel_rejected_reason").click(function () {
    clearOtherReasonError();
    $('#id_rejected-rejected_reason').val($('#old_predefined_rejected_reason').val());
    $('#id_rejected-other_reason').val($('#old_other_reason').val());
    if (otherSelected()){
        $('#id_rejected-other_reason').prop('disabled', false);
    }else{
        $('#id_rejected-other_reason').prop('disabled', true);
    }
    setStateActive(state_initial);
});

$("#id_rejected-rejected_reason").change( function() {
	disabledEnabledOtherReasonInputText2();
});