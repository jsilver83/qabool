$(function () {
    $("input[type=checkbox]").removeClass("form-control");
    searchable($("#id_searchable").val());
    $("#id_searchable").change(function () {
        searchable($(this).val());
    })
});

function searchable(val) {
    if (val == 'False') {
        $(".form_update").hide();
    }
    else {
        $(".form_update").show();
    }
}