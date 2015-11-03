function displayImg() {
    var reader = new FileReader();

    reader.onload = function (e) {
        // get loaded data and render thumbnail.
        document.getElementById("upload-img").src = e.target.result;
    };

    // read the image file as a data URL.
    reader.readAsDataURL(this.files[0]);
}

$(document).ready(function () {
    // Display the image when we choose a file
    document.getElementById("upload-file").onchange = displayImg
});
