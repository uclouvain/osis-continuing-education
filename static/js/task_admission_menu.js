
$("#id_check_all_admissions_to_accept").click(function(){
    if($("#id_check_all_admissions_to_accept:checked").length<=0){
        btn_actions_admissions_disabled();
    }else{
        btn_actions_admissions_enabled();
    }
});

$(".selected_admissions_to_accept").change(function(){
    menu_action_admission_status();

});

function menu_action_admission_status(){
    if($(".selected_admissions_to_accept:checked").length<=0){
        btn_actions_admissions_disabled();
    }else{
        btn_actions_admissions_enabled();
    }

}

function btn_actions_admissions_disabled(){
    $('#btn_tasks_admissions_actions').prop('disabled', true);
    $('#btn_tasks_admissions_actions').addClass('disabled');
    $('#div_admission_actions_btn').prop('title', "{%  trans 'Select registration first!' %}");
}

function btn_actions_admissions_enabled(){
    $('#btn_tasks_admissions_actions').prop('disabled', false);
    $('#btn_tasks_admissions_actions').removeClass('disabled');
    $('#div_admission_actions_btn').prop('title', '');
}

$(document).ready(function() {
    if($(".selected_admissions_to_accept:checked").length<=0){
        btn_actions_admissions_disabled();
    }else{
        btn_actions_admissions_enabled();
    }

});