function imageChosen() {
  var reader = new FileReader();

  reader.onload = function (e) {
    // get loaded data and render thumbnail.
    document.getElementById("upload-img").src = e.target.result;
  };

  // read the image file as a data URL.
  reader.readAsDataURL(this.files[0]);

  $(this).fileExif(function (exifObject) {
    console.log("fn");
    console.log(exifObject);
  });

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
    center: new google.maps.LatLng(10.397, 10.644),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  var markers = [];

  google.maps.event.addListener(map, 'bounds_changed', function() {
    loadImages(map, markers);
  });
}

function showImage(map, marker, markers) {
  console.log(marker);
  var infowindow = new google.maps.InfoWindow({
    content: '<IMG BORDER="0" ALIGN="Left" SRC="/media/' + marker.image.image + '">' + marker.position.toString()
  });
  for (var i = 0; i < markers.length; ++i) {
    if (markers[i].infoWindow != undefined) {
      markers[i].infoWindow.close();
    }
  }
  infowindow.open(map, marker);
  marker.infoWindow = infowindow;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addMarkers(map, markers, json) {
    console.log(markers.length);
    for (var i = 0; i < markers.length; ++i) {
      markers[i].setMap(null);
    }
    markers.length = 0;
    for (var i = 0; i < json.length; ++i) {
      var image = json[i];
      var latitude = image['lat'];
      var longitude = image['lng'];
      var latlng = new google.maps.LatLng({lat:latitude, lng:longitude});
      var marker = new google.maps.Marker({
        position:latlng,
        map:map
      });
      marker.image=image;
      markers.push(marker);
      var key = i;

      google.maps.event.addListener(markers[key],'mouseover', function(key2) {
        return function() {
          showImage(map, markers[key2], markers);
        }
      }(key));
    }
}

function loadImages(map, markers) {
  var bounds = map.getBounds();
  var latlngNE = map.getBounds().getNorthEast();
  var latlngSW = map.getBounds().getSouthWest();
  var latN = latlngNE.lat();
  var latS = latlngSW.lat();
  var lngE = latlngNE.lng();
  var lngW = latlngSW.lng();

  var csrftoken = getCookie('csrftoken');

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
  });

  $.ajax({
      type: "POST",
      url: "/get_images",
      data: {"latN":latN,"latS":latS,"lngE":lngE,"lngW":lngW},

      success: function(json) {
          addMarkers(map, markers, json);
      },
      error: function(json) {
          console.log(json);
      }
  });
  // get images as JSON object
  // show images on the map
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
