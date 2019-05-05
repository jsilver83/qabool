$(function () {
    $(".subBtn").hide();
    $('.concurr').prop('checked', false);
    $(".concurr").click(function () {
        $(".subBtn").toggle();
    });

    sm($("#id_nationality").val());
    $("#id_nationality").change(function () {
        var vaa = $(this).val();
        sm(vaa);
    });
    hs_sys_change($("#id_high_school_system").val());
    $("#id_high_school_system").change(function () {
        var vaa = $(this).val();
        hs_sys_change(vaa);
    });
    $("input[type=radio][name=saudi_mother]").change(function () {
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

    if ( $('ul.errors-tba li').length > 1 ) {
        alert($('.alert-tba').html());
    }
});

function sm(nat) {
    if (nat == 'SA') {
        $("#div_id_saudi_mother").hide();
        $("input[type=radio][name=saudi_mother]").prop('checked', false)
        $("input[type=radio][name=saudi_mother]").removeAttr("required");

        $("#div_id_saudi_mother_gov_id").hide();
        $("#id_saudi_mother_gov_id").val("");
        $("#id_saudi_mother_gov_id").removeAttr("required");
    }
    else if (nat == null || nat == "") {
        $("#div_id_saudi_mother").hide();
        $("#div_id_saudi_mother_gov_id").hide();
    }
    else {
        $("#div_id_saudi_mother").show();
        $("input[type=radio][name=saudi_mother]").attr("required", "required");

        if ($("input[type=radio][name=saudi_mother]:checked").val() == 'True') {
            $("#id_saudi_mother_gov_id").parents(".form-group").show();
            $("#id_saudi_mother_gov_id").attr("required", "");
        }
        else{
            $("#id_saudi_mother_gov_id").val("");
            $("#id_saudi_mother_gov_id").parents(".form-group").hide();
            $("#id_saudi_mother_gov_id").removeAttr("required");
        }
    }
}

function hs_sys_change(hs_sys) {
    var ht = $("#div_id_high_school_certificate label").html();

    if (hs_sys == 'INTERNATIONAL') {
        $("#div_id_high_school_certificate").show();
        ht = ht.trim();
        $("#div_id_high_school_certificate label").html(ht+"*");
        $("#div_id_high_school_certificate input").attr('required', 'required');
        $("#div_id_courses_certificate").show();
    }
    else {
        $("#id_high_school_certificate").val("");
        $("#id_courses_certificate").val("");

        $("#div_id_high_school_certificate").hide();
        $("#div_id_high_school_certificate label").html(ht.substring(0, ht.length-1));
        $("#div_id_high_school_certificate input").removeAttr('required');
        $("#div_id_courses_certificate").hide();
    }
}
