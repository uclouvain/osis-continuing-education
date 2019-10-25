//reuse address
let address = {
    location: "{{admission.address.location | escapejs}}",
    postal_code: "{{admission.address.postal_code | escapejs}}",
    city: "{{admission.address.city | escapejs}}",
    country: "{{admission.address.country_id | escapejs}}",
};
var billing_address = {
    location: "{{admission.billing_address.location | escapejs}}",
    postal_code: "{{admission.billing_address.postal_code | escapejs}}",
    city: "{{admission.billing_address.city | escapejs}}",
    country: "{{admission.billing_address.country_id | escapejs}}",
};
let residence_address = {
    location: "{{admission.residence_address.location | escapejs}}",
    postal_code: "{{admission.residence_address.postal_code | escapejs}}",
    city: "{{admission.residence_address.city | escapejs}}",
    country: "{{admission.residence_address.country_id | escapejs}}",
};

$("[name='use_address_for_billing']:radio").change(function(){
    if(this.value ==  "True"){
        copy_address("billing");
    } else {
        empty_address("billing", billing_address);
    }
});
// check when page is loaded
$("[name='use_address_for_billing']:radio").prop('checked')?copy_address("billing"):empty_address(("billing"), billing_address);

$("[name='use_address_for_post']:radio").change(function(){
    if(this.value ==  "True"){
        copy_address("residence");
    } else {
        empty_address("residence", residence_address);
    }
});
//check when page is loaded
$("[name='use_address_for_post']:radio").prop('checked')?copy_address("residence"):empty_address(("residence"), residence_address);
let fields_to_enable = ["birth_country", "billing-country", "residence-country", "gender"];
//re-enable disabled field on form submit
$( "#form" ).submit(function( event ) {
    enableFields(fields_to_enable);
});

function copy_address(e){
    ["location", "postal_code", "city"].forEach(function(field) {
        $("#id_"+e+"-"+field).val(address[field]);
        $("#id_"+e+"-"+field).prop("readonly", true);
    });
    $("#id_"+e+"-country").val(address['country']);
    $("#id_"+e+"-country").prop("disabled", true);
}

function empty_address(e, address){
    ["location", "postal_code", "city"].forEach(function(field) {
        $("#id_"+e+"-"+field).val(address[field]);
        $("#id_"+e+"-"+field).prop("readonly", false);
    });
    $("#id_"+e+"-country").val(address['country']);
    $("#id_"+e+"-country").prop("disabled", false);
}

$("#btn_confirm_fields").click(function(){
    $('#form').submit();
});

function enableFields(fields) {
    for (var field of fields) {
        $("#id_" + field).prop( "disabled", false );
    }
}
