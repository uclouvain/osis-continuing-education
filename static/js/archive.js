$("#id_check_all").click(function(){
    $('input:checkbox.selected_object').not(this).prop('checked', this.checked);
});

$("#btn_archive").click(function(e) {
    var url = $(this).attr('data-url');
    $("#admissions_form").attr("action", url);
    $("#admissions_form").submit();
});

