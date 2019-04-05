
function check_mandatory_fields(newState) {

    $.ajax({
        url: $(this).attr('data-url'),
        data: $(this).serialize(),
        context: this,
        success: function (responseData) {

            if (responseData) {
                if (Object.keys(responseData).length > 0) {

                    $('ul#list_fields_missing').empty();
                    for (var key in responseData) {
                        $('ul#list_fields_missing').prepend($("<li></li>").text(responseData[key]['verbose_name']));
                    }
                    $('#modal_confirm').modal('show');
                }else{
                    registration_submitted_confirmed(newState);

                }

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

$('button[name="btn_save"]').click(function(){
    if (check_mandatory_fields_in_screen()){
        $('#form').submit();
    }
});

function form_submit() {
    $('#form').submit();
}

function check_mandatory_fields_in_screen() {
    $('ul#list_fields_missing').empty();

    $('.participant_required').each(function () {
        if (!$(this).val()) {
            $('ul#list_fields_missing').prepend($("<li></li>").text($('label[for="' + $(this).attr('id') + '"]').text()));
        }
    });

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
