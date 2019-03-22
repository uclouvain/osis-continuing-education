$("#id_check_all").click(function(){
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});

$("#btn_activate").click(function(e) {
    $("#new_state").val("True");
    $("#formations_form").submit();
});

$("#btn_disable").click(function(e) {
    $("#new_state").val("False");
    $("#formations_form").submit();
});

$("#btn_training_aid_yes").click(function(e) {
    $("#new_training_aid_value").val("True");
    $("#formations_form").submit();
});

$("#btn_training_aid_no").click(function(e) {
    $("#new_training_aid_value").val("False");
    $("#formations_form").submit();
});
