var map;
var markerclusterer;
var allmarkers;
var imagecount=0;
// For now, just do the get once
var gotInsta = false;
var next_insta_url = '';

var markerclustererpublic;
var allmarkerspublic;
var imagepubliccount=0;

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
    zoomControl: true
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

  markerclustererpublic = new MarkerClusterer(map, [], clustererOptions);

  allmarkerspublic = [];

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
