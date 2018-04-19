$(function () {
    $(".subBtn").hide();
    $('.concurr').prop('checked', false);
    $(".concurr").click(function () {
        $(".subBtn").toggle();
    });

    sm($("#id_nationality").prop('selectedIndex'));
    $("#id_nationality").change(function () {
        var vaa = $(this).prop('selectedIndex');
        sm(vaa);
    });
    $("#id_saudi_mother").change(function () {
        var vaa = $("#id_nationality").prop('selectedIndex');
        sm(vaa);
    });
    $("textarea").addClass("form-control");

    $('.nocopy').bind('copy paste cut', function (e) {
        e.preventDefault(); //disable cut,copy,paste
        //alert('cut,copy & paste options are disabled !!');
    });

    $('#id_gender').hide();
    $('.field-gender .help-block').attr('style', 'color:red');
});

function sm(nat) {
    if (nat == 1) {
        $("#id_saudi_mother").parents(".form-group").hide();
        $("#id_saudi_mother").val("");
        $("#id_saudi_mother").removeAttr("required");

        $("#id_saudi_mother_gov_id").parents(".form-group").hide();
        $("#id_saudi_mother_gov_id").val("");
        $("#id_saudi_mother_gov_id").removeAttr("required");
    }
    else if (nat == null || nat == "") {
        $("#id_saudi_mother").parents(".form-group").hide();
        $("#id_saudi_mother_gov_id").parents(".form-group").hide();
    }
    else {
        $("#id_saudi_mother").parents(".form-group").show();
        $("#id_saudi_mother").attr("required", "");

        if ($("#id_saudi_mother").val() == 'True') {
            $("#id_saudi_mother").val("True");
            $("#id_saudi_mother_gov_id").parents(".form-group").show();
            $("#id_saudi_mother_gov_id").attr("required", "");
        }
        else{
            $("#id_saudi_mother").val("False");
            $("#id_saudi_mother_gov_id").val("");
            $("#id_saudi_mother_gov_id").parents(".form-group").hide();
            $("#id_saudi_mother_gov_id").removeAttr("required");
        }
    }
}