function register_user(event) {
  event.preventDefault();
  var form = $("#register-form");
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
    data: form.serialize(),
    success: function (data) {
      // Stop the spinner
      spinner.stop();
      var msg = $('#register-notification');

      if (data.errors.length > 0) {
        msg.html(data.errors[0]);
        msg.addClass("error");
      } else {
        // Reload the page, user should be authenticated now
        location.reload();
      }
      msg.removeClass("hidden");
    },
    error: function (data) {
      // Stop the spinner
      spinner.stop();
      console.log(data);
      msg.html("Error communicating with Geosnapr server! Try again soon?");
      msg.addClass("error");
      msg.removeClass("hidden");
    }
  });
}

$(document).ready(function(){
  // Start the carousel
  $('.background-carousel').slick({
    autoplay: true,
    autoplaySpeed: 3000
  });

  $.event.special.hoverintent = {
    setup: function() {
      $( this ).bind( "mouseover", jQuery.event.special.hoverintent.handler );
    },
    teardown: function() {
      $( this ).unbind( "mouseover", jQuery.event.special.hoverintent.handler );
    },
    handler: function( event ) {
      var currentX, currentY, timeout,
        args = arguments,
        target = $( event.target ),
        previousX = event.pageX,
        previousY = event.pageY;

      function track( event ) {
        currentX = event.pageX;
        currentY = event.pageY;
      };

      function clear() {
        target
          .unbind( "mousemove", track )
          .unbind( "mouseout", clear );
        clearTimeout( timeout );
      }

      function handler() {
        var prop,
          orig = event;

        if ( ( Math.abs( previousX - currentX ) +
            Math.abs( previousY - currentY ) ) < 7 ) {
          clear();

          event = $.Event( "hoverintent" );
          for ( prop in orig ) {
            if ( !( prop in event ) ) {
              event[ prop ] = orig[ prop ];
            }
          }
          // Prevent accessing the original event since the new event
          // is fired asynchronously and the old event is no longer
          // usable (#6028)
          delete event.originalEvent;

          target.trigger( event );
        } else {
          previousX = currentX;
          previousY = currentY;
          timeout = setTimeout( handler, 100 );
        }
      }

      timeout = setTimeout( handler, 100 );
      target.bind({
        mousemove: track,
        mouseout: clear
      });
    }
  };

  $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
      $(document).foundation('abide', 'reflow');
      $("#register-form").on('valid.fndtn.abide', register_user);
  });

  $( "#accordion" ).accordion({
    event: "click hoverintent",
    header: "div.accheader",
    collapsible: true,
    active: false,
    height: "auto"
  });

  $("#accordion").mouseleave(function() {
    $(this).accordion({
      active: false,
    });
  });
});
