$(function () {
    $("input[type=checkbox]").removeClass("form-control");
    searchable($("#id_searchable").val());
    $("#id_searchable").change(function () {
        searchable($(this).val());
    })

    $("label[for=id_sleeping]").html($("label[for=id_sleeping]").html() + " *");
    $("label[for=id_light]").html($("label[for=id_light]").html() + " *");
    $("label[for=id_room_temperature]").html($("label[for=id_room_temperature]").html() + " *");
    $("label[for=id_visits]").html($("label[for=id_visits]").html() + " *");
});

function searchable(val) {
    if (val == 'False') {
        $(".form_update").hide();

        $("#id_agree1").prop("checked", true);
        $("#id_agree2").prop("checked", true);
        $("#id_agree3").prop("checked", true);
    }
    else {
        $(".form_update").show();

        $("#id_agree1").prop("checked", false);
        $("#id_agree2").prop("checked", false);
        $("#id_agree3").prop("checked", false);
    }
}