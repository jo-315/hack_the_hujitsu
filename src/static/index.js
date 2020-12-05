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
    // Google MAP Data の取り出し
    console.log(response)

    // elementに渡す
    document.getElementById("total_steps").innerHTML = total_steps + steps
    document.getElementById("steps").innerHTML = 0
  });

}, 3000);
