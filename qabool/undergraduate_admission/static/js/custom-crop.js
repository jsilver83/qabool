$(function () {
    $("input[type=submit]").hide();

    /* SCRIPT TO OPEN THE MODAL WITH THE PREVIEW */
    $("#id_personal_picture").change(function () {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $("#image").attr("src", e.target.result);
                $("#modalCrop").modal("show");
            }
            reader.readAsDataURL(this.files[0]);
        }
    });

    /* SCRIPTS TO HANDLE THE CROPPER BOX */
    var $image = $("#image");
    var cropBoxData;
    var canvasData;
    $("#modalCrop").on("shown.bs.modal", function () {
        $(".modal .modal-body").css('overflow-y', 'auto');
        $(".modal .modal-body").css('max-height', $(window).height() * 0.8);
        $('.modal .modal-body').css('height', $(window).height() * 0.75);

        $image.cropper({
            viewMode: 1,
            aspectRatio: 4 / 5,
            minCropBoxWidth: 200,
            minCropBoxHeight: 200,
            ready: function () {
                $image.cropper("setCanvasData", canvasData);
                $image.cropper("setCropBoxData", cropBoxData);
            }
        });
    }).on("hidden.bs.modal", function () {
        cropBoxData = $image.cropper("getCropBoxData");
        canvasData = $image.cropper("getCanvasData");
        $image.cropper("destroy");
    });

    $(".js-zoom-in").click(function () {
        $image.cropper("zoom", 0.1);
    });

    $(".js-zoom-out").click(function () {
        $image.cropper("zoom", -0.1);
    });

    $(".js-rotate-right").click(function () {
        $image.cropper("rotate", 3);
    });

    $(".js-rotate-left").click(function () {
        $image.cropper("rotate", -3);
    });
});

function cropData() {
    var $image = $("#image");
    var cropDataURI = $image.cropper('getCroppedCanvas').toDataURL('image/jpeg', 0.9);//("getDataURL", "image/jpeg");
    $("#id_data_uri").val(cropDataURI);
}