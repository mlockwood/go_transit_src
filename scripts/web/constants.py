ORDER = ['Sunday - Thursday', 'Monday - Friday', 'Friday & Saturday', 'Saturday & Sunday', 'directions']

ROUTE_SCRIPT = """
      function initialize(){{
        var map = new google.maps.Map(document.getElementById('map'), {{
            center: {{lat: 47.10863333333334, lng: -122.55411111111111}},
            zoom: 15
        }});

        var rtURL = 'https://raw.githubusercontent.com/GOLewis-McChord/go_src/master/static/kml/route{}.kml?dummy='+(new Date()).getTime();
        var rtLayer = new google.maps.KmlLayer({{
          url: rtURL,
          map: map
        }});
        rtLayer.setMap(map)

        var stopURL = 'https://raw.githubusercontent.com/GOLewis-McChord/go_src/master/static/kml/stops.kml?dummy='+(new Date()).getTime();
        var stopLayer = new google.maps.KmlLayer({{
          url: stopURL,
          map: map
        }});
        stopLayer.setMap(map)

        google.maps.event.addListener(map, "click", function(event) {{
            var lat = event.latLng.lat();
            var lng = event.latLng.lng();
            // populate yor box/field with lat, lng
            alert("Lat=" + lat + "; Lng=" + lng);
        }});
      }}
"""
