
function check_mandatory_fields(newState) {

    $.ajax({
        url: $(this).attr('data-url'),
        data: $(this).serialize(),
        context: this,
        success: function (responseData) {

            if (responseData && Object.keys(responseData).length > 0) {

                $('ul#list_fields_missing').empty();
                for (var key in responseData) {
                    $('ul#list_fields_missing').append($("<li></li>").text(responseData[key]));
                }
                $('#modal_confirm').modal('show');

            } else {
                registration_submitted_confirmed(newState);
            }

        },
    });
}

function registration_submitted_confirmed(newState) {
    setStateActive(newState);
    $('#id_state').val(newState);
    $('#form').submit();
}

$('button[name="btn_save_registration"]').click(function(){
    if (check_mandatory_fields_in_screen()){
        $('#form').submit();
    }
});

$('button[name="btn_save"]').click(function(){
    $('#form').submit();
});

function form_submit() {
    $('#form').submit();
}

function check_mandatory_fields_in_screen() {
    $('ul#list_fields_missing').empty();

    $('.participant_required').each(function () {
        if ($(this).attr("id") && !$(this).val()) {
            var extra='';
            var div =$(this).closest('div[id]');

            if ($(this).attr("id").includes("_residence-") || $(this).attr("id").includes("_billing-")){
                extra =div.attr('name');
                extra = extra + " : " ;
            }

            $('ul#list_fields_missing').append($("<li></li>").text(extra + $('label[for="' + $(this).attr('id') + '"]').text()));
        }
    });

    if($('#id_national_registry_number').val().trim()=='' &&  $('#id_id_card_number').val().trim()=='' && $('#id_passport_number').val().trim()==''){
        var msg = $('#msg_required').html();
        $('ul#list_fields_missing').append($("<li></li>").text(msg + $('label[for="required_identification"]').text()));
    }

    if ($("ul#list_fields_missing").children('li').length > 0) {
        sortUL("ul#list_fields_missing");
        $('#modal_confirm').modal('show');
        return false;
    }else{
        return true;
    }
}

function sortUL(selector) {
    $(selector).children("li").sort(function(a, b) {
        var upA = $(a).text().toUpperCase();
        var upB = $(b).text().toUpperCase();
        return (upA < upB) ? -1 : (upA > upB) ? 1 : 0;
    }).appendTo(selector);
}
