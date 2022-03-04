
const addresses_variables = [];
if (typeof(billing_address) !== 'undefined') addresses_variables.push(
    {using: 'use_address_for_billing', address_type: 'billing', address_instance: billing_address}
);
if (typeof(residence_address) !== 'undefined') addresses_variables.push(
    {using: 'use_address_for_post', address_type: 'residence', address_instance: residence_address}
);
for(let {using, address_type, address_instance} of addresses_variables) {
    $("[name=" + using + "]:radio").change(function () {
        if (this.value === "True") {
            reset_error_in_address(address_type);
            copy_address(address_type);
        } else {
            empty_address(address_type, address_instance)
        }
    });
    $("[name=" + using + "]:radio").prop('checked') ? copy_address(address_type) : empty_address(address_type, address_instance);
}
let fields_to_enable = ["birth_country", "billing-country", "residence-country", "gender"];
//re-enable disabled field on form submit
$("#form").submit(function (event) {
    enableFields(fields_to_enable);
});

function copy_address(e) {
    ["location", "postal_code", "city"].forEach(function (field) {
        $("#id_" + e + "-" + field).val(address[field]);
        $("#id_" + e + "-" + field).prop("readonly", true);
    });
    $("#id_" + e + "-country").val(address['country']);
    $("#id_" + e + "-country").prop("disabled", true);
}

function empty_address(e, address) {
    ["location", "postal_code", "city"].forEach(function (field) {
        $("#id_" + e + "-" + field).val(address[field]);
        $("#id_" + e + "-" + field).prop("readonly", false);
    });
    $("#id_" + e + "-country").val(address['country']);
    $("#id_" + e + "-country").prop("disabled", false);
}

$("#btn_confirm_fields").click(function () {
    $('#form').submit();
});

function enableFields(fields) {
    for (var field of fields) {
        $("#id_" + field).prop("disabled", false);
    }
}

function reset_error_in_address(address_type){
    const classToRemove = 'has-error';
    const classOfDivToBeRemoved = 'help-block';
    var divAddress = document.getElementById(address_type+'_address');
    var divChildren = divAddress.getElementsByTagName("DIV");
    for (var i=0;i<divChildren.length;i++) {
        if (divChildren[i].classList.contains(classToRemove)) {
            divChildren[i].classList.remove(classToRemove);
            var elt_help_block = divChildren[i].getElementsByTagName("DIV");
            for (var j = 0; j < elt_help_block.length; j++) {
                if (elt_help_block[j].classList.contains(classOfDivToBeRemoved)) {
                    elt_help_block[j].remove();
                }
            }

        }
    }
}
