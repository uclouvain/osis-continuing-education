function openModal(idReasonModal, reason, otherReason) {
    $('#'+idReasonModal).modal('show');
    $('#'+reason.Old).val($('#'+reason.New).val());
    if (otherReason){
        $('#'+otherReason.Old).val($('#'+otherReason.New).val());
    }

}

function disabledEnabledOtherReasonInputText(elementIdReason, otherReasonId){
    if(otherSelected(elementIdReason)){
        document.getElementById(otherReasonId).disabled = false;
    }else{
        document.getElementById(otherReasonId).disabled = true;
        $(otherReasonId).val('');
        clearOtherReasonError();
    }
}

function otherSelected(elementIdReason){
    let selected_element = document.getElementById(elementIdReason).value;
    return selected_element === "Other" || selected_element === "Autre";
}

function clearOtherReasonError(otherReasonId){
    $('#' + otherReasonId).parent().removeClass("has-error");
}

function add_reason(otherReasonId, elementIdReason, idReasonModal, idForm){
    clearOtherReasonError(otherReasonId);
    if(!$('#'+otherReasonId).val() && otherSelected(elementIdReason)){
        $('#'+otherReasonId).parent().addClass("has-error");
    } else {
        $('#'+idForm).submit();
        $("#"+idReasonModal).modal('hide');
    }
}

function cancel_reason(otherReasonId, oldOtherReasonId,elementIdReason, elementIdOldReason){
    clearOtherReasonError(otherReasonId);

    $('#'+elementIdReason).val($('#'+elementIdOldReason).val());
    $('#'+otherReasonId).val($('#'+oldOtherReasonId).val());

    if (otherSelected(elementIdReason)){
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
        'old_predefined_waiting_reason'
    )
});

$("#cancel_rejected_reason").click(function(){
    cancel_reason(
        'id_rejected-other_reason',
        'old_rejected_other_reason',
        'id_rejected-rejected_reason',
        'old_predefined_rejected_reason'
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
