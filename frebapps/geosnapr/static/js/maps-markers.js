// hides the image info window of the marker
function hideImageInfoWindow(marker) {
  if (marker.infoWindow != undefined) {
    marker.infoWindow.close();
  }
}

// shows the image info window of the marker
function showImageInfoWindow(map, marker) {
  // creates new info window for the marker if it does not exist
  // opens it if it already exists
  if (marker.infoWindow != undefined) {
    console.log("already created");
    marker.infoWindow.open();
  }
  else {
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
    marker.infoWindow = infobubble;
  }
}

// add markers to the map
function addMarkers(json, public = false) {
  var markerarray;
  var imagecounter;

  if (public == false) {
    markerarray = allmarkers;
    imagecounter = imagecount;
  }
  else {
    markerarray = allmarkerspublic;
    imagecounter = imagepubliccount;
  }

  // adds each image object in the json object to the markerclusterer
  for (var i = 0; i < json.length; i++) {
    var image = json[i];
    var latitude = image['lat'];
    var longitude = image['lng'];
    var id = image['id'];
    var albums = image['albums'];
    currentUsername = image['username'];

    var latlng = new google.maps.LatLng({lat:latitude, lng:longitude});
    // creates new marker
    var marker = new google.maps.Marker({
      position:latlng,
      icon: 'static/img/marker_picture_small.png'
    });

    marker.image = image;
    marker.photoid = id;

    markerarray.push(marker);
    if (public == true) {
      markerclustererpublic.addMarker(marker);
    }
  }

  if (public == true) {
    imagecounter = 0;
  }

  for (var i = 0; i < json.length; ++i) {
    var markers = markerarray;
    var key = imagecounter;

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
    imagecounter++;
  }

  if (public == false) {
    show_album();
  }

  var markers2;
  if (public == false) {
    markers2 = markerclusterer.getMarkers();
  }
  if (public == true) {
    markers2 = markerclustererpublic.getMarkers();
  }

  // rezooms based on what was added
  if (markers2.length > 0) {
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markers2.length; ++i) {
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
