var fetch_step = setInterval(function(){
  latitude = document.getElementById("latitude").innerHTML
  longitude = document.getElementById("longitude").innerHTML
  steps = document.getElementById("steps").innerHTML
  total_steps = document.getElementById("total_steps").innerHTML

  const params = {
    latitude: latitude,
    longitude: longitude,
    steps: steps
  };

  const qs = new URLSearchParams(params);

  // fetch api でlocalhostと通信
  fetch(`/fetch?${qs}`, {
    method: "GET"
  })
  .then((response) => {
    return response.json();
  })
  .then((response) => {
    // map_url = response.map_url
    n_latitude = response.n_latitude
    n_longitude = response.n_longitude

    // Google MAP のURLをフロントに渡す
    // document.getElementById("google_map").src = map_url

    // elementに渡す
    document.getElementById("total_steps").innerHTML = parseInt(total_steps, 10) + parseInt(steps, 10)
    document.getElementById("steps").innerHTML = 0
  });

}, 3000);
