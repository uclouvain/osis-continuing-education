
function prepare_xls(e, action_value){
    e.preventDefault();
    var status = $("#xls_status");
    status.val(action_value);
    $("#search_form").submit();
    status.val('');
}