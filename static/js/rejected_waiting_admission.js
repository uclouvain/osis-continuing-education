function openModal(id_reason_modal, id_reason, id_old_reason, id_other_reason, id_old_other_reason) {
    $('#'+id_reason_modal).modal('show');
    $('#'+id_old_reason).val($('#'+id_reason).val());
    $('#'+id_old_other_reason).val($('#'+id_other_reason).val());
}

function disabledEnabledOtherReasonInputText(elementId_reason, otherReasonId){
    if(otherSelected(elementId_reason)){
        document.getElementById(otherReasonId).disabled = false;
    }else{
        document.getElementById(otherReasonId).disabled = true;
        $(otherReasonId).val('');
        clearOtherReasonError();
    }
}

function otherSelected(elementId_reason){
    let selected_element = document.getElementById(elementId_reason).value;
    return selected_element === "Other" || selected_element === "Autre";
}

function clearOtherReasonError(otherReasonId){
    $('#' + otherReasonId).parent().removeClass("has-error");
}

function add_reason(otherReasonId, elementId_reason, id_reason_modal, id_form){
    clearOtherReasonError(otherReasonId);
    if(!$('#'+otherReasonId).val() && otherSelected(elementId_reason)){
        $('#'+otherReasonId).parent().addClass("has-error");
    } else {
        $('#'+id_form).submit();
        $("#"+id_reason_modal).modal('hide');
    }
}

function cancel_reason(otherReasonId, oldOtherReasonId,elementId_reason, elementId_old_reason){
    clearOtherReasonError(otherReasonId);
    console.log($('#'+elementId_old_reason).val());
    console.log($('#'+oldOtherReasonId).val());

    $('#'+elementId_reason).val($('#'+elementId_old_reason).val());
    $('#'+otherReasonId).val($('#'+oldOtherReasonId).val());

    if (otherSelected(elementId_reason)){
        $('#'+otherReasonId).prop('disabled', false);
    }else{
        $('#'+otherReasonId).prop('disabled', true);
    }
    setStateActive(state_initial);
}

$('#add_waiting_reason').click(function(){
    add_reason(
        'id_other_reason',
        'id_waiting_reason',
        'waiting_reason_modal',
        'form'
    )
});

$('#add_rejected_reason').click(function(){
    add_reason(
        'id_rejected-other_reason',
        'id_rejected-rejected_reason',
        'rejected_reason_modal',
        'form'
    )
});


$("#cancel_waiting_reason").click(function(){
    cancel_reason(
        'id_other_reason',
        'old_other_reason',
        'id_waiting_reason',
        'old_predefined_waiting_reason',
    )
});

$("#cancel_rejected_reason").click(function(){
    cancel_reason(
        'id_rejected-other_reason',
        'old_rejected_other_reason',
        'id_rejected-rejected_reason',
        'old_predefined_rejected_reason',
    )
});

$("#id_rejected-rejected_reason").change( function() {
	disabledEnabledOtherReasonInputText(
	    "id_rejected-rejected_reason",
        "id_rejected-other_reason");
});

$("#id_waiting_reason").change( function() {
	disabledEnabledOtherReasonInputText(
	    "id_waiting_reason",
        "id_other_reason");
});
