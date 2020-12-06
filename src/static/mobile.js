var GRAVITY_MIN = 9.8;
var GRAVITY_MAX = 12.00;

var _step = 0;

var _isStep = false;

// https://qiita.com/kwst/items/5bd0c2e6c2c8ceb406e5

function onDeviceMotion(e) {
    e.preventDefault();

    // 重力加速度を取得
    var ag = e.accelerationIncludingGravity;
    // 重力加速度ベクトルの大きさを取得
    var acc = Math.sqrt(ag.x*ag.x + ag.y*ag.y + ag.z*ag.z);

    if (_isStep) {
        // 歩行中にしきい値よりも低ければ一歩とみなす
        if (acc < GRAVITY_MIN) {
            _step++;
            _isStep = false;
        }
    } else {
        // しきい値よりも大きければ歩いているとみなす
        if (acc > GRAVITY_MAX) {
            _isStep = true;
        }
    }
}

function post_steps(){
    setInterval(function(){
        fetch('/mobiledata',{
            method: 'POST',
            body: _step
        });
        console.log("POST /mobiledata" + _step);
    }, 3000);
}