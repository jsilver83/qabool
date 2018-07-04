$(function(){
    try{
        $(".datepicker").datepicker({
            dateFormat: 'yy-mm-dd',
            changeMonth: true,
            changeYear: true,
            yearRange: "1980:2040",
        });
    }catch(e){}
    $(".nav-tabs li").each(function(){
        if($(this).hasClass("active")){
            $(this).find("a").html("<strong>" + $(this).find("a").html() + "</strong>");
        }
    });
    $("input[type=file]").removeClass("form-control");
    try{
        $(".hijri").calendarsPicker({calendar: $.calendars.instance('ummalqura', 'ar'),dateFormat: 'dd-mm-yyyy'});
    }catch(e){}

    $(".updateOnce").each(function(){
        if($(this).val().length > 0 && $(this).val() != null){
            $(this).attr("readonly", "");
        }
    });

    employed($("input[name=is_employed]:checked").val());
    $("input[name=is_employed]").change(function(){
        employed($(this).val());
    });

    disability($("input[name=is_disabled]:checked").val());
    $("input[name=is_disabled]").change(function(){
        disability($(this).val());
    });

    diseases($("input[name=is_diseased]:checked").val());
    $("input[name=is_diseased]").change(function(){
        diseases($(this).val());
    });

    have_a_vehicle($("input[name=have_a_vehicle]:checked").val());
    $("input[name=have_a_vehicle]").change(function(){
        have_a_vehicle($(this).val());
    });

//    $("input").change(function(){
//        alert("test");
//        alert($("#disability_needs").val());
//    });
//    alert("test");
});

function employed(value){
    if(value == "True"){
        $(".field-employment").parents(".form-group").show();
        $("input[name=employment]").attr("required", "");
        $(".field-employer_name").parents(".form-group").show();
        $(".field-employer_name input").attr("required", "");
    }
    else{
        $(".field-employment").parents(".form-group").hide();
        $("input[name=employment]").removeAttr("required", "");
        $(".field-employer_name").parents(".form-group").hide();
        $(".field-employer_name input").removeAttr("required", "");
    }
}

function disability(value){
    if(value == "True"){
        $(".field-disability_needs").parents(".form-group").show();
//        $("input[name=disability_needs]").attr("required", "");
        $(".field-disability_needs_notes").parents(".form-group").show();
    }
    else{
        $(".field-disability_needs").parents(".form-group").hide();
//        $("input[name=disability_needs]").removeAttr("required", "");
        $(".field-disability_needs_notes").parents(".form-group").hide();
    }
}

function diseases(value){
    if(value == "True"){
        $(".field-chronic_diseases").parents(".form-group").show();
//        $("input[name=chronic_diseases]").attr("required", "");
        $(".field-chronic_diseases_notes").parents(".form-group").show();
    }
    else{
        $(".field-chronic_diseases").parents(".form-group").hide();
//        $("input[name=chronic_diseases]").removeAttr("required", "");
        $(".field-chronic_diseases_notes").parents(".form-group").hide();
    }
}

function have_a_vehicle(value){
    if(value == "True"){
        $(".field-vehicle_owner").parents(".form-group").show();
        $(".field-vehicle_plate_no").parents(".form-group").show();
        $(".field-vehicle_registration_file").parents(".form-group").show();
        $(".field-driving_license_file").parents(".form-group").show();
    }
    else{
        $("#id_vehicle_owner").val("");
        $(".field-vehicle_owner").parents(".form-group").hide();
        $("#id_vehicle_plate_no").val("");
        $(".field-vehicle_plate_no").parents(".form-group").hide();
        $(".field-vehicle_registration_file").parents(".form-group").hide();
        $(".field-driving_license_file").parents(".form-group").hide();
    }
}

//function disability(value){
//    if(value == "True"){
//            $(".field-disability_needs").parents(".form-group").show();
//            $("#id_disability_needs").attr("required", "");
//            $(".field-disability_needs_notes").parents(".form-group").show();
//        }
//        else{
//            $(".field-disability_needs").parents(".form-group").hide();
//            $("#id_disability_needs").removeAttr("required", "");
//            $(".field-disability_needs_notes").parents(".form-group").hide();
//        }
//}
//
//function diseases(value){
//    if(value == "True"){
//            $(".field-chronic_diseases").parents(".form-group").show();
//            $("#id_chronic_diseases").attr("required", "");
//            $(".field-chronic_diseases_notes").parents(".form-group").show();
//        }
//        else{
//            $(".field-chronic_diseases").parents(".form-group").hide();
//            $("#id_chronic_diseases").removeAttr("required", "");
//            $(".field-chronic_diseases_notes").parents(".form-group").hide();
//        }
//}