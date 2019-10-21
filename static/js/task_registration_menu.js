
$("#id_check_all_registrations_to_validate").click(function(){
    if($("#id_check_all_registrations_to_validate:checked").length<=0){
        btn_actions_registrations_disabled();
    }else{
        btn_actions_registrations_enabled();
    }
});

$(".selected_registrations_to_validate").change(function(){
    menu_action_registration_status();

});

function menu_action_registration_status(){
    alert($(".selected_registrations_to_validate:checked").length);
    if($(".selected_registrations_to_validate:checked").length<=0){
        btn_actions_registrations_disabled();
    }else{
        btn_actions_registrations_enabled();
    }

}

function btn_actions_registrations_disabled(){
    $('#btn_tasks_registrations_actions').prop('disabled', true);
    $('#btn_tasks_registrations_actions').addClass('disabled');
    $('#div_registration_actions_btn').prop('title', "{%  trans 'Select registration first!' %}");
}

function btn_actions_registrations_enabled(){
    $('#btn_tasks_registrations_actions').prop('disabled', false);
    $('#btn_tasks_registrations_actions').removeClass('disabled');
    $('#div_registration_actions_btn').prop('title', '');
}

$(document).ready(function() {
    if($(".selected_registrations_to_validate:checked").length<=0){
        btn_actions_registrations_disabled();
    }else{
        btn_actions_registrations_enabled();
    }
});