var map;
var markerclusterer;
var allmarkers;
var imagecount=0;
// For now, just do the get once
var gotInsta = false;
var next_insta_url = '';

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

function show_album() {
  var id = $('#map-albums').val();
  markerclusterer.clearMarkers();

  if (id == 1) {
    markerclusterer.addMarkers(allmarkers);
    markerclusterer.repaint();
  }
  else {
    $.ajax({
      type: "POST",
      url: "get_album",
      data: {'a_id':id},
      success: function(data) {
        var images = data.images;
        for (var i = 0; i < allmarkers.length; i++) {
          var marker = allmarkers[i];
          var check = parseInt(marker.photoid);
          if (images.indexOf(check) > -1) {
            markerclusterer.addMarker(marker);
          }
        }
        markerclusterer.repaint();
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

// Maps functions

function initialize() {
  var mapOptions = {
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    zoom: 16,
    minZoom: 3, // most the map can zoom out
    maxZoom: 20, // most the map can zoom in
    center: new google.maps.LatLng(40, -79),
    mapTypeControl: false,
    streetViewControl: false,
    zoomControl: false
  };

  map = new google.maps.Map(document.getElementById('map-canvas'),
    mapOptions);

  // changes icon for the cluster icon
  var markerstyles = [{url: '/static/img/marker_album_small.png',
                        height: 64,
                        width: 64}]
  var clustererOptions = {
    styles: markerstyles,
    zoomOnClick: false
  }

  markerclusterer = new MarkerClusterer(map, [], clustererOptions);

  allmarkers = [];

  google.maps.event.addListenerOnce(map, 'bounds_changed', function() {
    loadImages(map);
  });

  // creates objects for map location search
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

  // creates objects for image location search
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

  $('#imagelocation').keydown(function (e) {
    if (e.which == 13 && $('.pac-container:visible').length) return false;
  });

  // creates objects for image edit location search
  var imageeditinput = (document.getElementById('imageeditlocation'));
  var imageeditautocomplete = new google.maps.places.Autocomplete(imageeditinput);

  imageeditautocomplete.addListener('place_changed', function() {
    var place = imageeditautocomplete.getPlace();
    if (place.geometry) {
      var latform = document.getElementById("autoeditlat");
      var lngform = document.getElementById("autoeditlng");
      latform.value = place.geometry.location.lat();
      lngform.value = place.geometry.location.lng();
    };
  });

  google.maps.event.addListener(markerclusterer, 'mouseover', function(cluster) {
    var markers = cluster.getMarkers();
    var content = "<div class='infowindow-container'>";

    for (var i = 0; i < markers.length; ++i) {
      var marker = markers[i]
      if (i % 3 == 0) {
        var htmlcontent = `
          <div class="row">
          <div class="columns large-4 thumbnail-container">
            <img border="0" class="thumbnail" src="` + marker.image.image + `">
            <p>` + marker.image.caption + `</p>
          </div>`;
        content = content + htmlcontent;
      }
      else if (i % 3 == 1) {
        var htmlcontent = `
          <div class="columns large-4 thumbnail-container">
            <img border="0" class="thumbnail" src="` + marker.image.image + `">
            <p>` + marker.image.caption + `</p>
          </div>`;
        content = content + htmlcontent;
      }
      else if (i % 3 == 2) {
        var htmlcontent = `
          <div class="columns large-4 thumbnail-container">
            <img border="0" class="thumbnail" src="` + marker.image.image + `">
            <p>` + marker.image.caption + `</p>
          </div>
          </div>`;
        content = content + htmlcontent;
      }
    };

    if (markers.length % 3 == 1) {
      htmlcontent = `
        <div class="columns large-4 thumbnail-container">
        </div>
        <div class="columns large-4 thumbnail-container">
        </div>
        </div></div>`;
      content = content + htmlcontent;
    }

    if (markers.length % 3 == 2) {
      htmlcontent = `<div class="columns large-4 thumbnail-container">
              </div></div></div>`;
      content = content + htmlcontent;
    }

    var infobubble = new InfoBubble({
      disableAutoPan: true,
      hideCloseButton: true,
      borderWidth: 0,
      padding: 0,
      content: content,
      position: (cluster.getCenter()),
      pixelOffset: [0,32]
    });

    infobubble.open(map);
    cluster.infoWindow = infobubble;
  });

  google.maps.event.addListener(markerclusterer, 'mouseoff', function(cluster) {
    if (cluster.infoWindow != undefined) {
      cluster.infoWindow.close();
    }
  });

  google.maps.event.addListener(map, 'zoom_changed', function() {
    var clusters = markerclusterer.getClusters();
    for (var i = 0; i < clusters.length; ++i) {
      var cluster = clusters[i];
      if (cluster.infoWindow != null) {
        cluster.infoWindow.close();
      }
    }
  })

  $(document).on('opened.fndtn.reveal', '[data-reveal]', function() {
    $('.album-carousel').slick({
      autoplay:true,
      autoplaySpeed: 3000
    });
  });

  $(document).on('closed.fndtn.reveal', '[data-reveal]', function() {
    $('.album-carousel').slick("unslick");
  })


  google.maps.event.addListener(markerclusterer, 'clusterclick', function(cluster) {
    var markers = cluster.getMarkers();
    var htmlcontent = "";
    if (cluster.infoWindow != null) {
        cluster.infoWindow.close();
    }

    for (var i = 0; i < markers.length; ++i) {
      var marker = markers[i];
      var content = `<div data-id="` + i + `"><div class="row">
<div class="columns large-8">
<img src="`+ marker.image.image + `"/></div>
<div class="columns large-4">
<p>` + marker.image.caption + `</p>
</div>
</div></div>`;
      htmlcontent = htmlcontent + content;

    }
    $('#albumcarousel').empty();
    $('#albumcarousel').on('click', '.slick-slide', function () {
      var id = $(this).attr('data-id');
      openImageEditForm(markers[id].image);
    });
    $('#albumcarousel').append(htmlcontent);
    $('#album-modal').foundation('reveal','open');
  });

  $("#map-albums").change(function() {
    show_album();
  });
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

function hideImageInfoWindow(marker) {
  // should always be defined if function is called
  if (marker.infoWindow != undefined) {
    marker.infoWindow.close();
  }
}

function showImageInfoWindow(map, marker) {
  var htmlcontent = `
  <div class="thumbnail-container">
    <img border="0" class="thumbnail" src="` + marker.image.image + `">
  </div>`;

  var infobubble = new InfoBubble({
    maxWidth: 300,
    minWidth: 300,
    content: htmlcontent,
    disableAutoPan: true,
    hideCloseButton: true,
    borderWidth: 0,
    padding: 0,
    pixelOffset: [0,0],
  })

  infobubble.open(map, marker);
  if (marker.infoWindow != undefined) {
    marker.infoWindow.close();
  }
  marker.infoWindow = infobubble;
}

function addMarkers(json) {
  // adds each image object in the json object to the markerclusterer
  for (var i = 0; i < json.length; i++) {
    var image = json[i];
    var latitude = image['lat'];
    var longitude = image['lng'];
    var id = image['id'];
    var albums = image['albums'];

    var latlng = new google.maps.LatLng({lat:latitude, lng:longitude});
    // creates new marker
    var marker = new google.maps.Marker({
      position:latlng,
      icon: 'static/img/marker_picture_small.png'
    });

    marker.image = image;
    marker.photoid = id;

    allmarkers.push(marker);
  }

  for (var i = 0; i < json.length; ++i) {
    var markers = allmarkers;
    var key = imagecount;

    google.maps.event.addListener(markers[key],'mouseover', function(key2) {
      return function() {
        showImageInfoWindow(map, markers[key2]);
      }
    }(key));

    google.maps.event.addListener(markers[key],'mouseout', function(key2) {
      return function() {
        hideImageInfoWindow(markers[key2]);
      }
    }(key));

    google.maps.event.addListener(markers[key],'click', function(key2) {
      return function() {
        var image = markers[key2].image;
        openImageEditForm(image);
      }
    }(key));


    imagecount++;
  }
  show_album();
  var markers2 = markerclusterer.getMarkers();

  // rezooms based on what was added
  if (markers2.length > 0) {
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markers.length; ++i) {
      var marker = markers2[i];
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

function loadImages(map) {
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
          addMarkers(json);
      },
      error: function(json, error) {
          console.log(json);
          console.log(error);
      }
  });
}

function loadScript() {
  console.log('loading');
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyCBBymT1deOyItH-JCJdSX5nL0VpH1mHes&libraries=places&callback=initialize";
  document.body.appendChild(script);
}

function getInstaImages() {
  var url = "/get_insta_images?next=" + encodeURIComponent(next_insta_url);
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
        next_insta_url = data.next_insta_url;
        for (i = 0; i < data.photos.length; i++) {
          var photo = data.photos[i];
          var div = document.createElement('div');
          var img = document.createElement('img');
          img.setAttribute('data-lazy', photo.image);
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

        //Callback to get more instagram images
        if (next_insta_url != '') {
          $("#insta-images").children(".slick-next").click(function() {
            var slick = parent.slick('getSlick');
            if ((slick.slideCount - slick.currentSlide) == slick.options.slidesToShow) {
              getInstaImages();
            }
          });
        }
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
    geocodeForm(lat,lng,$("#autolat"), $("#autolng"), $('#imagelocation'));

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

      // Create album form submit
      $("#create-album-form").on('valid.fndtn.abide', create_album);

      // Edit profile submit
      $("#edit-profile-form").on('valid.fndtn.abide', edit_profile);

      // Multiple select
      $("#upload-album").select2({
        width: "100%"
      });

      // Multiple select
      $("#edit-album").select2({
        width: "100%"
      });
    });

    // Submit image form
    $("#upload-img-btn").on('click', upload_image);

    // Load insta images on toggled tab
    $("#panel2").on('toggled', function(e, tab) {
      $("#insta-images").slick('setPosition');

      if (!gotInsta && !($("#insta-link").length)) {
        getInstaImages();
        gotInsta = true;
      }
    });

    // Set up slick for instagram
    $("#insta-images").slick({
      infinite: false,
      slidesToShow: 3,
      slidesToScroll: 1,
      lazyLoad: 'ondemand'
    });

    $('#insta-images').on('click', '.slick-slide', toggleSelectedImage);

    $("#map-albums").select2();

    $("#delete-image").on('click', delete_image);
});
