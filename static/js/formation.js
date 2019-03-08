$("#id_check_all").click(function(){
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});

$("#btn_activate").click(function(e) {
    $("#new_state").val(true);
    $("#formations_form").submit();
});

$("#btn_disable").click(function(e) {
    $("#new_state").val(false);
    $("#formations_form").submit();
});
