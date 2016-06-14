$(function(){
    $(".datepicker").datepicker({
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
        yearRange: "1990:2016",
    });
    $(".nav-tabs li").each(function(){
        if($(this).hasClass("active")){
            $(this).find("a").html("<strong>" + $(this).find("a").html() + "</strong>");
        }
    });
    $("input[type=file]").removeClass("form-control");
    $(".hijri").calendarsPicker($.extend(
        {calendar: $.calendars.instance('ummalqura', 'ar')},
        $.calendarsPicker.regionalOptions['ar']));
    $('.hijri').change(function() {
        calendar = $.calendars.instance($(this).val());
        var convert = function(value) {
            return (!value || typeof value != 'object' ? value :
                calendar.fromJD(value.toJD()));
        };
        $('.is-calendarsPicker').each(function() {
            var current = $(this).calendarsPicker('option');
            $(this).calendarsPicker('option', {calendar: calendar,
                    onSelect: null, onChangeMonthYear: null,
                    defaultDate: convert(current.defaultDate),
                    minDate: convert(current.minDate),
                    maxDate: convert(current.maxDate)}).
                calendarsPicker('option',
                    {onSelect: current.onSelect,
                    onChangeMonthYear: current.onChangeMonthYear});
        });
    });

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