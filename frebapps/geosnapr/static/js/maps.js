var map;
var markers;
var imagecount=0;
// For now, just do the get once
var gotInsta = false;

///////////////////////////////
// Alert functions
///////////////////////////////

function fadeAlert() {
  var msg = $("#message");
  msg.fadeOut(500, function () {
    msg.removeClass();
    msg.addClass("alert-box");
    msg.html();
  });
}

function alertSuccess(content) {
  var msg = $("#message");
  msg.addClass("success");
  msg.html(content);
  msg.fadeIn(500);

  // Fade the alert
  setTimeout(fadeAlert, 3000);
}

function geocodeForm(lat, lng) {
  $("#autolat").val(lat);
  $("#autolng").val(lng);

  // Try to reverse geocode
  var geocoder = new google.maps.Geocoder;
  var loc = {
    lat: lat,
    lng: lng
  };

  geocoder.geocode({'location': loc}, function(results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      if (results[1]) {
        var placeInput = $('#imagelocation');
        placeInput.val(results[1].formatted_address);
      }
    } else {
      console.log("Geocoder failed due to: " + status);
    }
  });
}

function imageChosen(input) {
  var reader = new FileReader();

  reader.onload = function (e) {
    // get loaded data and render thumbnail.
    document.getElementById("upload-img").src = e.target.result;
  };

  // read the image file as a data URL.
  reader.readAsDataURL(input.files[0]);

  $(input).fileExif(function (exifObject) {
    console.log(exifObject);

    if (exifObject.GPSLatitude && exifObject.GPSLongitude) {
      var latArray = exifObject.GPSLatitude;
      var lngArray = exifObject.GPSLongitude;

      // Convert lat/lng to decimal
      var latDecimal = latArray[0] + (latArray[1]/60) + (latArray[2]/3600);

      var lngDecimal = lngArray[0] + (lngArray[1]/60) + (lngArray[2]/3600);

      // N/S/E/W
      if (exifObject.GPSLatitudeRef === "S") {
        latDecimal = latDecimal * -1;
      }
      if (exifObject.GPSLongitudeRef === "W") {
        lngDecimal = lngDecimal * -1;
      }

      geocodeForm(latDecimal, lngDecimal);
    }
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

      if (data.errors.length > 0) {
        msg.html(data.errors[0]);
        msg.addClass("error");
      } else {
        alertSuccess(data.msg);
        // Close the modal
        $('#editProfileModal').foundation('reveal', 'close');
      }
      msg.removeClass("hidden");
    },
    error: function (data) {
      console.log(data);
    }
  });
}

function clearImageForm() {
  $("#autolat").val('');
  $("#autolng").val('');
  $("#imagelocation").val('');
  $("#caption").val('');
}

function upload_image(event) {
  event.preventDefault();
  var form = $("#upload-img-form");
  var formData = new FormData(document.getElementById("upload-img-form"));
  // Are we in the instagram tab?
  if ($("#panel2").attr('aria-hidden') == 'false') {
    formData.append('external', true);
    formData.append('url', $("#selected-img").attr('src'));
  }
  // Set up the loading spinner
  var opts = {
    scale: 2.5,
    top: '50%',
    left: '50%'
  };
  var spinner = new Spinner(opts).spin();

  // Show the loading spinner
  form.append(spinner.el);

 $.ajax({
    type: form.attr('method'),
    url: form.attr('action'),
    data: formData,
    processData: false,
    contentType: false,
    success: function (data) {
      // Add a new marker
      addMarkers(map, markers, [data.image]);
      // Remove the form data
      clearImageForm();
      //$("#upload-img").val(null);
      $("#upload-img").attr('src', '');
      $("#upload-file").replaceWith($("#upload-file").clone(true));
      // Close the modal
      $('#uploadModal').foundation('reveal', 'close');
      // Stop the spinner
      spinner.stop();
      alertSuccess(data.message);
    },
    error: function (data) {
      console.log(data);
      console.log("fail");
    }
  });

}

function create_album() {
  event.preventDefault();
  var form = $("#create-album-form");
  var formData = new FormData(document.getElementById("create-album-form"));

  // Set up the loading spinner
  var opts = {
    scale: 2.5,
    top: '50%',
    left: '50%'
  };
  var spinner = new Spinner(opts).spin();

  // Show the loading spinner
  form.append(spinner.el);

  $.ajax({
    type: form.attr('method'),
    url: form.attr('action'),
    data: formData,
    processData: false,
    contentType: false,
    success: function(data) {
      // Append the new album to the dropdown
      var option = document.createElement('option');
      option.value = data.album.id;
      option.innerHTML = data.album.name;
      $("#albums").append(option)
      // Clear the form data
      $("album-name").val('')
      // Close the modal
      $('#uploadModal').foundation('reveal', 'close');
      // Stop the spinner
      spinner.stop();
      alertSuccess(data.message);
    },
    error: function(data) {

    }
  });
}

// Maps functions

function initialize() {
  var mapOptions = {
    zoom: 8,
    center: new google.maps.LatLng(40, -79),
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false,
    streetViewControl: false
  };

  map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  markers = [];

  google.maps.event.addListenerOnce(map, 'bounds_changed', function() {
    loadImages(map, markers);
  });

  // creates objects for autcomplete search fields
  var input = (document.getElementById('locationsearch'));
  var autocomplete = new google.maps.places.Autocomplete(input);
  autocomplete.bindTo('bounds', map);

  autocomplete.addListener('place_changed', function() {
    var place = autocomplete.getPlace();
    if (place.geometry) {
      map.setCenter(place.geometry.location);
      map.setZoom(8);
    }
  });

  var imageinput = (document.getElementById('imagelocation'));
  var imageautocomplete = new google.maps.places.Autocomplete(imageinput);

  imageautocomplete.addListener('place_changed', function() {
    var place = imageautocomplete.getPlace();
      if (place.geometry) {
        var latform = document.getElementById("autolat");
        var lngform = document.getElementById("autolng");
        latform.value = place.geometry.location.lat();
        lngform.value = place.geometry.location.lng();
      }
  });
}

function hideImage(map, marker, markers) {
  for (var i = 0; i < markers.length; ++i) {
    if (markers[i].infoWindow != undefined) {
      markers[i].infoWindow.close();
    }
  }
}

function showImage(map, marker, markers) {
  var infowindow = new google.maps.InfoWindow({
    content: '<img border="0" height="42" class="thumbnail" src="' + marker.image.image + '">' +"\n" + "<p>" + marker.image.caption + "</p>"
  });
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
      var key = imagecount;

      google.maps.event.addListener(markers[key],'mouseover', function(key2) {
        return function() {
          showImage(map, markers[key2], markers);
        }
      }(key));
      google.maps.event.addListener(markers[key],'mouseout', function(key2) {
        return function() {
          hideImage(map, markers[key2], markers);
        }
      }(key));
      imagecount = imagecount+1;
    }
    if (markers.length > 0) {
      var bounds = new google.maps.LatLngBounds();
      for (var i = 0; i < markers.length; ++i) {
        var marker = markers[i];
        bounds.extend(marker.position);
      }
      map.fitBounds(bounds);
      var listener = google.maps.event.addListenerOnce(map, "idle", function() {
          if (map.getZoom() > 8) map.setZoom(8);
      });
    }
    else {
      map.setCenter(new google.maps.LatLng(40, -79));
      map.setZoom(8);
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
  script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCBBymT1deOyItH-JCJdSX5nL0VpH1mHes&libraries=places&callback=initialize";
  document.body.appendChild(script);
}

function getInstaImages() {
  var url = "/get_insta_images";
  var parent = $('#insta-images');
  // Set up the spinner
  var opts = {
    top: '40px',
    left: '25%'
  }
  var spinner = new Spinner(opts).spin();

  // Show the loading spinner
  parent.append(spinner.el);
  $.ajax({
    type: "GET",
    url: url,

    success: function(data) {
      if (data.error) {
        console.log(data.error);
      } else {
        for (i = 0; i < data.photos.length; i++) {
          var photo = data.photos[i];
          var div = document.createElement('div');
          var img = document.createElement('img');
          img.src = photo.image;
          img.setAttribute('data-lat', photo.lat);
          img.setAttribute('data-lng', photo.lng);
          img.setAttribute('data-caption', photo.caption);
          $(img).addClass('slick-img');
          //img.onclick = toggleSelectedImage;
          div.appendChild(img);
          parent.slick('slickAdd',div);
        }
        // Stop the spinner
        spinner.stop();
      }
    },
    error: function(data) {
      spinner.stop();
      console.log(data);
    }
  });
}

function toggleSelectedImage() {
  var current = $("#selected-img");

  var img = $(this).children("img")
  img.attr('id', "selected-img");
  current.attr('id', "");

  if (img.attr('id') == 'selected-img') {
    $("#img-loc-form").removeClass("hidden");
    clearImageForm();
    var lat = parseFloat(img.attr('data-lat'));
    var lng = parseFloat(img.attr('data-lng'));
    // Fill the form with data
    geocodeForm(lat,lng);

    $("#caption").val(img.attr('data-caption'));
  } else {
    $("#img-loc-form").addClass("hidden");
  }
}

// Set up all bindings

$(document).ready(function () {
    //Display the image when we choose a file
    $("#upload-file").on('change', function() {
      if (this.value != null) {
        imageChosen(this);
      }
    });

    loadScript();

    $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
      $(document).foundation('abide', 'reflow');
      $(document).foundation('tab', 'reflow');
      $("#edit-profile-form").on('valid.fndtn.abide', edit_profile);
      $("#upload-img-btn").on('click', upload_image);
      $("#create-album-form").on('valid.fndtn.abide', create_album);
    });

    // Load insta images on toggled tab
    $("#panel2").on('toggled', function(e, tab) {
      $("#insta-images").slick('setPosition');
      if (!gotInsta) {
        getInstaImages();
        gotInsta = true;
      }
    });

    // Set up slick for instagram
    $("#insta-images").slick({
      infinite: true,
      slidesToShow: 3,
      slidesToScroll: 1,
    });

    $('#insta-images').on('click', '.slick-slide', toggleSelectedImage);
});
