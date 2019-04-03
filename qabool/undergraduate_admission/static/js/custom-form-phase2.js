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
        $("#div_id_employer_name").show();
        $("#div_id_employer_name input").attr("required", "");
    }
    else{
        $("#div_id_employer_name").hide();
        $("#div_id_employer_name input").removeAttr("required", "");
    }
}

function disability(value){
    if(value == "True"){
        $("#div_id_disability_needs").show();
        $("#div_id_disability_needs_notes").show();
    }
    else{
        $("#div_id_disability_needs").hide();
        $("#div_id_disability_needs_notes").hide();
    }
}

function diseases(value){
    if(value == "True"){
        $("#div_id_chronic_diseases").show();
        $("#div_id_chronic_diseases_notes").show();
    }
    else{
        $("#div_id_chronic_diseases").hide();
        $("#div_id_chronic_diseases_notes").hide();
    }
}

function have_a_vehicle(value){
    if(value == "True"){
        $("#div_id_vehicle_owner").show();
        $("#div_id_vehicle_plate_no").show();
        $("#div_id_vehicle_registration_file").show();
        $("#div_id_driving_license_file").show();
    }
    else{
        $("input[name=vehicle_owner]").removeAttr("checked");
        $("#div_id_vehicle_owner").hide();
        $("#div_id_vehicle_plate_no input").val("");
        $("#div_id_vehicle_plate_no").hide();
        $("#div_id_vehicle_registration_file").hide();
        $("#div_id_driving_license_file").hide();
    }
}
