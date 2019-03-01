$("#id_check_all").click(function(){
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});

$("#btn_archive").click(function(e) {
    $("#admissions_form").submit();
});

