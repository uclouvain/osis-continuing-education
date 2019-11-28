
function check_mandatory_fields(newState) {

    $.ajax({
        url: $(this).attr('data-url'),
        data: $(this).serialize(),
        context: this,
        success: function (responseData) {

            if (responseData && Object.keys(responseData).length > 0) {

                $('ul#list_fields_missing').empty();
                for (let key in responseData) {
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
            let extra='';
            let div =$(this).closest('div[id]');

            if ($(this).attr("id").includes("_residence-") || $(this).attr("id").includes("_billing-")){
                extra =div.attr('name');
                extra = extra + " : " ;
            }

            $('ul#list_fields_missing').append($("<li></li>").text(extra + $('label[for="' + $(this).attr('id') + '"]').text()));
        }
    });
    const mandatory_fields = ['national_registry_number', 'id_card_number', 'passport_number'];
    const is_define = (field) => $('#id_' + field).val() !== undefined;
    if(mandatory_fields.every(is_define)) {
        const is_empty = (field) => $('#id_' + field).val().trim()
        if (mandatory_fields.every(is_empty)) {
            let msg = $('#msg_required').html();
            $('ul#list_fields_missing').append($("<li></li>").text(msg + $('label[for="required_identification"]').text()));
        }
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
        let upA = $(a).text().toUpperCase();
        let upB = $(b).text().toUpperCase();
        return (upA < upB) ? -1 : (upA > upB) ? 1 : 0;
    }).appendTo(selector);
}
