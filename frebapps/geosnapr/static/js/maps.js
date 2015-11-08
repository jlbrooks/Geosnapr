function imageChosen() {
  var reader = new FileReader();

  reader.onload = function (e) {
    // get loaded data and render thumbnail.
    document.getElementById("upload-img").src = e.target.result;
  };

  // read the image file as a data URL.
  reader.readAsDataURL(this.files[0]);

  $("#img-loc-form").removeClass("hidden");
}

function edit_profile(event) {
    event.preventDefault();
    var form = $("#edit-profile-form");
    
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(),
        success: function (data) {
            var msg = $('#profile-notification');
            console.log(data)
            if (data.errors.length > 0) { 
              msg.html(data.errors[0]);
              msg.addClass("error");
            } else {
              msg.html(data.msg);
              msg.addClass("success");
            }
            msg.removeClass("hidden");
        },
        error: function (data) {
            console.log(data);
        }
    })
}

// Maps functions

function initialize() {
  var mapOptions = {
    zoom: 8,
    center: new google.maps.LatLng(-34.397, 150.644),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);
}

function loadScript() {
  console.log('loading');
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCBBymT1deOyItH-JCJdSX5nL0VpH1mHes&callback=initialize";
  document.body.appendChild(script);
}

// Set up all bindings

$(document).ready(function () {
    // Display the image when we choose a file
    document.getElementById("upload-file").onchange = imageChosen;

    loadScript();

    $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
      $(document).foundation('abide', 'reflow');
      $("#edit-profile-form").on('valid.fndtn.abide', edit_profile);
    });
});