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

function geocodeForm(lat, lng, latElem, lngElem, resultElem) {
  $(latElem).val(lat);
  $(lngElem).val(lng);

  // Try to reverse geocode
  var geocoder = new google.maps.Geocoder;
  var loc = {
    lat: lat,
    lng: lng
  };

  geocoder.geocode({'location': loc}, function(results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      if (results[1]) {
        $(resultElem).val(results[1].formatted_address);
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

      geocodeForm(latDecimal, lngDecimal, $("#autolat"), $("#autolng"), $('#imagelocation'));
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
  if ($("#autolat").val() == '') {
    $("#img-loc-form").prepend('<div data-alert class="alert-box alert radius">\
      Location information is required.\
      <a href="#" class="close">&times;</a>\
    </div>');
    $(document).foundation();

    return;
  };
  if ($("#autolng").val() == '') {
    $("#img-loc-form").prepend('<div data-alert class="alert-box alert radius">\
      Location information is required.\
      <a href="#" class="close">&times;</a>\
    </div>');
    $(document).foundation();
    return;
  };
  formData.append("upload-album", $("#upload-album").val());
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
      addMarkers([data.image]);
      // Remove the form dataå
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

function delete_image() {
  event.preventDefault();
  var id = $("#img-id").val();
  var data = {
    "img_id": id
  }

  $.ajax({
    type: "POST",
    url: $(this).attr('href'),
    data: data,
    success: function (data) {
      // For now, redirect to this page
      location.reload();
    },
    error: function (data) {
      console.log(data);
    }
  })
}

function edit_image() {
  event.preventDefault();
  var form = $("#img-edit-form");
  var formData = new FormData(document.getElementById("img-edit-form"));
  if ($("#autoeditlat").val() == '') {
    $("#img-edit-form").prepend('<div data-alert class="alert-box alert radius">\
      Location information is required.\
      <a href="#" class="close">&times;</a>\
    </div>');
    $(document).foundation();

    return;
  };
  if ($("#autoeditlng").val() == '') {
    $("#img-edit-form").prepend('<div data-alert class="alert-box alert radius">\
      Location information is required.\
      <a href="#" class="close">&times;</a>\
    </div>');
    $(document).foundation();
    return;
  };

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
      for (var i = 0; i < allmarkers.length; i++) {
        var marker = allmarkers[i];
        if (marker.image.id == data.image.id) {

          marker.image.caption = data.image.caption;
          marker.image.lat = data.image.lat;
          marker.image.lng = data.image.lng;
          marker.image.albums = data.image.albums;
          var latlng = new google.maps.LatLng({lat:data.image.lat, lng:data.image.lng});
          marker.setPosition(latlng);
        }
      }

      show_album();
      // Close the modal
      $('#uploadModal').foundation('reveal', 'close');
      // Stop the spinner
      spinner.stop();
      alertSuccess(data.message);
    },
    error: function(data) {
      console.log('error');
      spinner.stop();
      console.log(data);
    }
  })
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
      var option = new Option(data.album.name, data.album.id);
      $(option).html(data.album.name);
      $("#map-albums").append(option);
      $("#upload-album").append($(option).clone());
      $("#edit-album").append($(option).clone());
      // Clear the form data
      $("#album-name").val('Untitled Album')
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

function openImageEditForm(image) {
  $("#img-edit-form-hidden").hide();
  $("#img-edit-form-show").show();
  $("#img-edit-form-show").on("click", function() {
    $("#img-edit-form-hidden").show();
    $("#img-edit-form-show").hide();
  });
  $('#photo-modal-link').attr("src",image.image.replace(/&amp;/g, '&'));
  $('#photo-modal-comment').text(image.caption);
  $("#editcaption").val(image.caption);
  $("#img-id").val(image.id);
  $("#edit-album").val(image.albums);
  geocodeForm(image.lat, image.lng, $("#autoeditlat"), $("#autoeditlng"), $('#imageeditlocation'));

  $('#photo-modal').foundation('reveal','open');
  $("#edit-img-btn").unbind('click');
  $("#edit-img-btn").on('click', edit_image);
}

function openImageViewForm(image) {
  $("#img-edit-form-hidden").hide();
  $("#img-edit-form-show").hide();
  $("#delete-image").hide();
  $('#photo-modal-link').attr("src",image.image.replace(/&amp;/g, '&'));
  $('#photo-modal-comment').text(image.caption);
  $('#photo-modal-user').text("Photo by: " + image.username);
  $('#photo-modal').foundation('reveal','open');
}

function show_album() {
  var id = $('#map-albums').val();
  console.log(id);
  markerclusterer.clearMarkers();
  markerclustererpublic.clearMarkers();

  if (id == 0) {
    $.ajax({
      type: "POST",
      url: "get_public",
      success: function(data) {
        console.log(data);
        var images = data.images;
        addMarkersPublic(images);

        var markers = markerclustererpublic.getMarkers();

        if (markers.length > 0) {
          console.log('resizing');
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
      },
      error: function(data) {
        console.log(data);
      }
    });
  }

  else {
    $.ajax({
      type: "POST",
      url: "get_album",
      data: {'a_id':id},
      success: function(data) {
        var images = data.images;

        // extracts the photos from the album to show
        for (var i = 0; i < allmarkers.length; i++) {
          var marker = allmarkers[i];
          var check = parseInt(marker.photoid);
          if (images.indexOf(check) > -1) {
            markerclusterer.addMarker(marker);
          }
        }

        var markers = markerclusterer.getMarkers();

        if (markers.length > 0) {
          console.log('resizing');
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
      },
      error: function(data) {
        console.log(data);
      }
    });
  }

}
