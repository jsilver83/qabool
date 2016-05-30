$(function(){
    $(".subBtn").hide();
    $('.concurr').prop('checked', false);
    $(".concurr").click(function(){
        $(".subBtn").toggle();
    });

    sm($("#id_nationality").prop('selectedIndex'));
    $("#id_nationality").change(function(){
        var vaa = $(this).prop('selectedIndex');
        sm(vaa);
    });
    $("textarea").addClass("form-control");
});

function sm(nat){
    if(nat == 1){
        $("#id_saudi_mother").parents(".form-group").hide();
        $("#id_saudi_mother").val("");
        $("#id_saudi_mother").removeAttr("required");
    }
    else if(nat == null || nat == ""){
        $("#id_saudi_mother").parents(".form-group").hide();
    }
    else{
        $("#id_saudi_mother").parents(".form-group").show();
        if($("#id_saudi_mother").val() != 'True'){
            $("#id_saudi_mother").val("False");
        }
        $("#id_saudi_mother").attr("required", "");
    }
}