function openModalAcceptance(idReasonModal, condition_acceptance) {
    $('#'+idReasonModal).modal('show');
    $('#'+condition_acceptance.Old).val($('#'+condition_acceptance.New).val());
}

$("#id_condition_of_acceptance_existing_0").click(function() {
    $("#id_condition_of_acceptance").prop('disabled', false);
});

$("#id_condition_of_acceptance_existing_1").click(function() {
    disabledEnabledTextField("id_condition_of_acceptance");
});

$("#cancel_condition_acceptance").click(function(){
    $('#id_condition_of_acceptance').parent().removeClass("has-error");
    if ($('#id_condition_of_acceptance_existing_1').prop('checked')){
        disabledEnabledTextField("id_condition_of_acceptance");
    }else{
        $('#id_condition_of_acceptance').val($('#old_condition_of_acceptance').val());
        $("#id_condition_of_acceptance").prop('disabled', false);

    }
    setStateActive(state_initial);
});

$('#add_condition_acceptance').click(function(){
    add_condition_acceptance_reason(
        'id_condition_of_acceptance_existing_0',
        'id_condition_of_acceptance',
        'form'
    )
});

function disabledEnabledTextField(id){
    $("#"+id).val('');
    $("#"+id).prop('disabled', true);
}

function add_condition_acceptance_reason(existingConditionId, elementIdReason, idForm) {
    if ($('#' + existingConditionId).prop('checked') && !$('#' + elementIdReason).val()) {
        $('#' + elementIdReason).parent().addClass("has-error");
    } else {
        $('#' + idForm).submit();
    }
}
