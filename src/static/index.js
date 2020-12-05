var fetch_step = setInterval(function(){
  latitude = 10
  longitude = 20
  // latitude = document.getElementById("latitude").innerHTML
  // longitude = document.getElementById("longitude").innerHTML
  const params = {
    latitude: latitude,
    longitude: longitude
  };
  const qs = new URLSearchParams(params);

  // fetch api でlocalhostと通信
  fetch(`http://localhost:5050/fetch?${qs}`, {
    method: "GET"
  })
  .then((response) => {
    return response.json();
  })
  .then((response) => {
    // Google MAP Data の取り出し

    // elementに渡す
    // document.getElementById("steps").innerHTML = steps
    // const fenway = { lat: 42.345573, lng: -71.098326 };
    // const map = new google.maps.Map(document.getElementById("map"), {
    //   center: fenway,
    //   zoom: 14,
    // });
    // const panorama = new google.maps.StreetViewPanorama(
    //   document.getElementById("pano"),
    //   {
    //     position: fenway,
    //     pov: {
    //       heading: 34,
    //       pitch: 10,
    //     },
    //   }
    // );
    // map.setStreetView(panorama);
  });

}, 3000);
