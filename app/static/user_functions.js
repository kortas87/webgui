var testVariable = 1;
var gauge1 = null;
var gauge4 = null;

var viewGaugeInit = false;

function view_gauge_init() {
  viewGaugeInit = true;
}

function view_gauge() {
  if (viewGaugeInit) {
    gauge1 = new Gauge("canvas1", { 'color': "#0F0" ,'range': {'min':0, 'max':100 } }); // gauge is not draw until Gauge.draw(value) runs; 
    gauge4 = new Gauge("canvas4", {'mode':'needle', 'range': {'min':0, 'max':140 } });
    viewGaugeInit = false;
  } else {
    gauge1.draw(Math.round(parseFloat(document.getElementById("stacksoc").innerHTML)));
    gauge4.draw(Math.round(parseFloat(document.getElementById("stackvolt").innerHTML)));
  }
}

