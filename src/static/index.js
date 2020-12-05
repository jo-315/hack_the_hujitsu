var fetch_step = setInterval(function(){
  // fetch api でlocalhostと通信
  fetch('http://localhost:5050/fetch', {
    method: "GET"
  })
  .then((response) => {
    return response.json();
  })
  .then((response) => {
    // 歩数の取り出し
    steps = response.steps

    // 歩数をelementに渡す
    document.getElementById("steps").innerHTML = steps

    return steps
  })
  .then((steps) => {
     // Google Map API 飛ばす？？
  })
  ;

}, 3000);

// TODO: google map api と通信？？