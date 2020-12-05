var fetch_step = setInterval(function(){
  latitude = document.getElementById("latitude").innerHTML
  longitude = document.getElementById("longitude").innerHTML
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
  });

}, 3000);
