$("#id_check_all").click(function(){
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});

$("#btn_activate").click(function(e) {
    $("#new_state").val("True");
    $("#new_training_aid_value").val("None");
    $("#formations_form").submit();
});

$("#btn_disable").click(function(e) {
    $("#new_state").val("False");
    $("#new_training_aid_value").val("None");
    $("#formations_form").submit();
});

$("#btn_training_aid_yes").click(function(e) {
    $("#new_training_aid_value").val("True");
    $("#new_state").val("None");
    $("#formations_form").submit();
});

$("#btn_training_aid_no").click(function(e) {
    $("#new_training_aid_value").val("False");
    $("#new_state").val("None");
    $("#formations_form").submit();
});
