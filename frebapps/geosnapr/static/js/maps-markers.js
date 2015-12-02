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

function addMarkersPublic(json) {

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
    allmarkerspublic.push(marker);
    markerclustererpublic.addMarker(marker);
  }

  imagepubliccount = 0;

  for (var i = 0; i < json.length; ++i) {
    var markers = allmarkerspublic;
    var key = imagepubliccount;

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


    imagepubliccount++;
  }

  var markers2 = markerclustererpublic.getMarkers();
  console.log("public");
  console.log(markers2);

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
