$('#add_cancel_reason').click(function(){
    console.log('ici')

    if(!$('#id_state_reason').val() ){
        $('#id_state_reason').parent().addClass("has-error");
    } else {
        $('#form').submit();
        $("#cancel_reason_modal").modal('hide');
    }
});

$("#cancel_cancel_waiting_reason").click(function(){
    $('#id_state_reason').val($('#old_cancel_reason').val());
    setStateActive(state_initial);
});

$("#lnk_state_admission_Cancelled").click(function(){
    $('#old_cancel_reason').val($('#id_state_reason').val());
    $('#id_state_reason').val('');
});
