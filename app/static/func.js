var t;
var tt;
var req=false;
function lion() { 
  req=false;
  function reqComplete(){ 
    if(req.readyState==4) {
      if(req.status==200) { 
        tt=setTimeout("loadingDisappear()",40);
        
        var values=req.responseText.split("\n");
        var f=0;
        var voltMax = 0;
        var voltMaxElem;
        var voltMin = 6;
        var voltMinElem;
        var volt;
        var voltHeight;
        var currentModule = 0;
        var nextModule;
        
        for (i=0;i<values.length;++i) {
          line = values[i].split("=");
          var htmlobj = document.getElementById(line[0]);
          //update value
        try {
          if (htmlobj.type == "text") {
            htmlobj.value=line[1];
          } else {
            htmlobj.innerHTML=line[1];
          }
        } catch(err) {
          alert(err.message+' line:'+line);
        }
          //CSS voltage + min,max
          if (line[0].substring(0,2) == "vm") {
            voltHeight = Math.round(280*(parseFloat(line[1])-2.4)/2);
            volt = parseFloat(line[1]);
            if(voltHeight>250) {
              voltHeight = 250;
            }
            if(voltHeight<10) {
              voltHeight = 10;
            }
            document.getElementById(line[0]).parentNode.parentNode.style.height=voltHeight;
            if(volt > voltMax) {
              voltMax = volt;
              voltMaxElem = document.getElementById(line[0]); 
            }
            if(volt < voltMin) {
              voltMin = volt;
              voltMinElem = document.getElementById(line[0]);
            }
          }
          //uptime format
          if (line[0].substring(0,6) == "uptime") {
            document.getElementById(line[0]).innerHTML = getReadableTime(line[1]);
          }
          if (line[0].substring(0,7) == "cputime") {
            document.getElementById(line[0]).innerHTML = getReadableTime(line[1]);
          }
          
          //CSS temperature
          if (line[0].substring(0,2) == "tm") {
            var tempHeight = Math.round(parseFloat(line[1]));
            if (tempHeight<10) {
              tempHeight = 10;
            }
            if(tempHeight>200) {
              tempHeight = 200;
            }
            document.getElementById(line[0]).style.height=tempHeight;
          }
          //CSS balancing
          if (line[0].substring(0,2) == "bm") {
            if (line[1]=="1") {
              document.getElementById(line[0]).style.display="inline";
            } else {
              document.getElementById(line[0]).style.display="none";
            }
          }
          //sound warning test
          if (line[0].substring(0,12) == "stackmaxcell") {
            if (3.6<parseFloat(line[1])) {
              if (document.getElementById('alarm_stackmaxcell').innerHTML != 'played') {
                document.getElementById('alarm_stackmaxcell').innerHTML = "played";
                playalarm();
              }
            } 
          }
          //alert
          if (line[0].substring(0,5) == "alert") {
            var newalert = document.getElementById("alert").innerHTML;
            if (newalert != document.getElementById("alertShown").innerHTML) {
              document.getElementById("alertShown").innerHTML = newalert;
              if(newalert != "") {
                alert(newalert);
              }
            }
          }
          
          //console
          if (line[0].substring(0,11) == "consoleHTML") {
            var console = document.getElementById("consoleOUTPUT");
            if (line[1].length > 0) {
              console.innerHTML += line[1];
              document.getElementById('consoleOUTPUT').scrollTop = document.getElementById('consoleOUTPUT').scrollHeight;
            }
          }
          
          
          
          //CSS error USB
          if (line[0].substring(0,6) == "status") {
            if (line[1].substring(0,9) != "connected") {
              var x = document.querySelectorAll(".module");
              for (j = 0; j < x.length; j++) {
                x[j].style.backgroundColor = '#444';
              }
            } else {
              var x =document.querySelectorAll(".module")
              for (j = 0; j < x.length; j++) {
                x[j].style.backgroundColor = '#eee';
              }
            }
            if (line[1].substring(0,5) == "retry") {
              document.getElementById('status').style.backgroundColor = '#f22';
            } else {
              document.getElementById('status').style.backgroundColor = '';
            }
          }
          //CSS error PIC (PEC percent > 5)
          if (line[0].substring(0,13) == "cpuPECpercent") {
            if (Math.round(parseFloat(line[1]))> 5) {
              document.body.style.background = '#f00';
            } else {
              document.body.style.background = '#ccc';
            }
          }
          
        } //for
        
        /* run user function if exists */
        viewname = document.getElementById('current-view').innerHTML;
        if (typeof window[viewname] === 'function') { 
          window[viewname]();
        }
        /**/
      }
    }
  }
  if(window.XMLHttpRequest) {
    req=new XMLHttpRequest();
  } else if(window.ActiveXObject) {
    req=new ActiveXObject("Microsoft.XMLHTTP");
  }
  if(req) {
    document.getElementById("refreshms").style.backgroundColor="red";
    req.open("GET", "/data/"+Math.round(100000000*Math.random())+"/"+document.getElementById('current-view').innerHTML, true);
    req.onreadystatechange=reqComplete;
    req.send(null);
  }
  refreshms=document.getElementById("refreshms").value*1000;
  if (refreshms < 1000) {
    refreshms = 1000;    
  }
  if (refreshms > 60000) {
    refreshms = 60000;    
  }
  document.getElementById("refreshms").value = refreshms/1000;
  t=setTimeout("lion()",refreshms);
}

function loadView(view) {

  //load content
  lionLoad("/view/"+view,'container');
  
  //save current view var
  document.getElementById('current-view').innerHTML = view;
  
  /* run user init function if exists */
  var funcname = view+'_init';
  if (typeof window[funcname] === 'function') { 
    window[funcname]();
  }
}


function loadingDisappear() {
  document.getElementById("refreshms").style.backgroundColor="white";    
}

function playalarm() {
  var audio = new Audio('/static/buzzer.mp3');
  //audio.play();  
}

function getReadableTime(num) {
  var output = '';
  var temp = Math.round(parseFloat(num));
  if (temp<60) {
    output = temp+'s';
  } else if (temp<3600) {
    var minute = Math.floor(temp/60);
    var second = temp % 60;
    output = minute+'m'+second+'s';
  } else {
    var hour = Math.floor(temp/3600);
    var minutes = temp % 3600;
    minute = Math.floor(minutes/60);
    var second = minutes % 60;
    output = hour+'h'+minute+'m'+second+'s';
  }
  return output;
}



function serverSend(data) {
  lionLoad("/"+data+"/"+Math.round(100000000*Math.random()),null);
}

function lionLoad(url,where) {
  reqX=false;
  function reqXComplete(){ 
    if(reqX.readyState==4) {
      if(reqX.status==200) {
        if (where != null) {
          document.getElementById(where).innerHTML = reqX.responseText;
        }
      }
    }
  }
  if(window.XMLHttpRequest) {
    reqX=new XMLHttpRequest();
  } else if(window.ActiveXObject) {
    reqX=new ActiveXObject("Microsoft.XMLHTTP");
  }
  if(reqX) {
    reqX.open("GET", url, true);
    reqX.onreadystatechange=reqXComplete;
    reqX.send(null);
  }
}






function toggleVisibility(what) {
  var obj = document.getElementById(what);
  if (obj.style.display == 'block') {
    obj.style.display='none';
  } else {
    obj.style.display='block';
  }
}




/* BmsLion module functions           */
/* in future move it to separate file */

function BmsLion_consoleSubmit() {
    var a = document.getElementById('consoleINPUT').value;
    serverSend("BmsLion/_/_/"+a);
    var elem = document.getElementById('consoleOUTPUT');
    elem.innerHTML+= a+'<br />';
    elem.scrollTop = elem.scrollHeight;
}


function BmsLion_hex2a() {
    var hex = document.getElementById("eepromOUT").value.toString();//force conversion
    var str = '';
    for (var i = 0; i < hex.length; i += 2)
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    
    alert(str);
}

function BmsLion_parseLittleEndian(hex) {
    var result = 0;
    var pow = 0;
    while (hex.length > 0) {
        result += parseInt(hex.substring(0, 2), 16) * Math.pow(2, pow);
        hex = hex.substring(2, hex.length);
        pow += 8;
    }
    return result;
};


function BmsLion_settingsLoad() {
  var data = document.getElementById("settingsOUT").value;
  var word = 0;
  var cell = 0;
  var id = '';
  
  //load cells + temperatures
  if (data.length == 232) { //TODO: change length...
    for (var i = 0; i < 120; i += 4) {
      if(i<72) {
        cell = i / 4;
      } else {
        cell = (i-72)/ 4;
      }
      word = BmsLion_parseLittleEndian(data.substr(i,4),16);
      for (var module = 0; module < 16; module++) {
        //if cell/temp  is set
        if(Math.pow(2, module) & word) {
          
          if(i<72) {
            //cell
            document.getElementById("vm"+module+"cs"+cell).innerHTML = "1";
          } else {
            //temp
            document.getElementById("tm"+module+"cs"+cell).innerHTML = "1";    
          }
        } else {
          if (i<72) {
            //cell
            document.getElementById("vm"+module+"cs"+cell).innerHTML = "0";
          } else {
            //temp
            document.getElementById("tm"+module+"cs"+cell).innerHTML = "0";    
          }
        }
      }
    }
    var regOffset = 4000;
    for (var reg = 30; reg < 58; reg++) {
      document.getElementById("set"+(regOffset+reg)).value = BmsLion_parseLittleEndian(data.substr(reg*4,4),16);
    }
    BmsLion_settingsRefresh();
  } else {
    alert('ERROR: Setting too short (not loaded?)\nString length: '+data.length);
  }
}

function BmsLion_settingsRefresh() {
  for (var module = 0; module < 16; module++) {
    for (var cell = 0; cell < 18; cell++) {
      //volt
      if(document.getElementById("vm"+module+"cs"+cell).innerHTML == "1") {
        document.getElementById("vm"+module+"cs"+cell).parentNode.style.backgroundColor = 'green';
      } else {
        document.getElementById("vm"+module+"cs"+cell).parentNode.style.backgroundColor = '#fff';
      }
      //temp
      if(document.getElementById("tm"+module+"cs"+cell).innerHTML == "1") {
        document.getElementById("tm"+module+"cs"+cell).parentNode.style.backgroundColor = 'orange';
      } else {
        document.getElementById("tm"+module+"cs"+cell).parentNode.style.backgroundColor = '#fff';
      }
    }
  }
  BmsLion_settingsCreate();
}

function BmsLion_struct() {
    var eeprom = document.getElementById("eepromOUT").value.toString();//force conversion
    
    var CounterRuntime = getReadableTime(BmsLion_parseLittleEndian(eeprom.substring(0,8),16));
    var CounterMakebreak = BmsLion_parseLittleEndian(eeprom.substring(8,16),16);
    var error1 = BmsLion_parseLittleEndian(eeprom.substring(16,18),16);
    var error2 = BmsLion_parseLittleEndian(eeprom.substring(18,20),16);
    var V_StackMaximum = BmsLion_parseLittleEndian(eeprom.substring(20,28),16);
    var V_StackMinimum = BmsLion_parseLittleEndian(eeprom.substring(28,36),16);
    var I_StackMaximum = BmsLion_parseLittleEndian(eeprom.substring(36,44),16);
    var I_StackMinimum = BmsLion_parseLittleEndian(eeprom.substring(44,52),16);
    I_StackMinimum = -1*(~I_StackMinimum);
    var V_CellMaximum = BmsLion_parseLittleEndian(eeprom.substring(52,56),16);
    var V_CellMinimum = BmsLion_parseLittleEndian(eeprom.substring(56,60),16);
    var T_CellMaximum = BmsLion_parseLittleEndian(eeprom.substring(60,64),16);
    var T_CellMinimum = BmsLion_parseLittleEndian(eeprom.substring(64,68),16);
    var CounterWrites = BmsLion_parseLittleEndian(eeprom.substring(68,72),16);
    var SOC = BmsLion_parseLittleEndian(eeprom.substring(72,76),16);
    
    var error1str = '';
    error1str += 'CellOvervoltage: '+((error1 & 1)  !=0 )+'\n';
    error1str += 'CellUndervoltage: '+((error1 & 2)  !=0 )+'\n';
    error1str += 'CellOverTemperature: '+((error1 & 4)  !=0 )+'\n';
    error1str += 'CellTempTooHigh: '+((error1 & 8)  !=0 )+'\n';
    error1str += 'CellTempTooHighToCharge: '+((error1 & 16)  !=0 )+'\n';
    error1str += 'CellTempTooLowToCharge: '+((error1 & 32)  !=0 )+'\n';
    error1str += 'VoltageDifferenceSumCells: '+((error1 & 64)  !=0 )+'\n';
    error1str += 'InternalCommunicationError: '+((error1 & 128) !=0 )+'\n';
    
    var error2str = '';
    error2str += 'MasterSlaveCommunicationError: '+((error2 & 1)  !=0 )+'\n';
    error2str += 'BatteryEmpty: '+((error2 & 2)  !=0 )+'\n';
    error2str += 'ShortCircuitDetected: '+((error2 & 4)  !=0 )+'\n';
    error2str += 'LeakDetected: '+((error2 & 8)  !=0 )+'\n';
    error2str += 'ContactorErrorMainsP: '+((error2 & 16)  !=0 )+'\n';
    error2str += 'ContactorErrorMainsN: '+((error2 & 32)  !=0 )+'\n';
    error2str += 'ContactorErrorPrecharge: '+((error2 & 64)  !=0 )+'\n';
    error2str += 'Not used: '+((error2 & 128) !=0 )+'\n';


    var output = 'CounterRuntime: '+CounterRuntime+'\n';
    output += 'CounterMakebreak: '+CounterMakebreak+'\n';
    output += 'CounterWrites: '+CounterWrites+'\n';
    output += 'SOC: '+SOC/100+'%\n';
    output += '----------------\n';
    output += 'V_StackMaximum: '+V_StackMaximum/10000+'V\n';
    output += 'V_StackMinimum: '+V_StackMinimum/10000+'V\n';
    output += 'I_StackMaximum: '+I_StackMaximum/10000+'A\n';
    output += 'I_StackMinimum: '+I_StackMinimum/10000+'A\n';
    output += 'V_CellMaximum: '+V_CellMaximum/10000+'V\n';
    output += 'V_CellMinimum: '+V_CellMinimum/10000+'V\n';
    output += 'T_CellMaximum: '+(T_CellMaximum-27315)/100+'°C\n';
    output += 'T_CellMinimum: '+(T_CellMinimum-27315)/100+'°C\n';
    output += '----------------\n';
    output += error1str;
    output += '----------------\n';
    output += error2str;
    output += '----------------\n';
 
    //alert(BmsLion_parseLittleEndian('9f000000'));
    alert(output);
}


function BmsLion_settingsCreate() {
  
  var word = 0;
  var settings = "";
  
  //volt
  for (var cell = 0; cell < 18; cell++) {
    for (var module = 0; module < 16; module++) {
      if(document.getElementById("vm"+module+"cs"+cell).innerHTML == "1") {
        word = word | (1 << module)
      }
    }
    settings += BmsLion_decimalToHexLittle(word, 4);
    word = 0;
  }
  
  //temperature
  for (var cell = 0; cell < 12; cell++) {
    for (var module = 0; module < 16; module++) {
      if(document.getElementById("tm"+module+"cs"+cell).innerHTML == "1") {
        word = word | (1 << module)
      }
    }
    settings += BmsLion_decimalToHexLittle(word, 4);
    word = 0;
  }
  
  var regOffset = 4000;
  for (var reg = 30; reg < 58; reg++) {
    settings += BmsLion_decimalToHexLittle(document.getElementById("set"+(regOffset+reg)).value, 4);
  }
  
  document.getElementById("settingsNEW").value = settings;
  document.getElementById("settingsLength").innerHTML = settings.length/2;
}
function BmsLion_decimalToHexLittle(d, padding) {
    var littleEndian = "";
    var hex = Number(d).toString(16);
    padding = typeof (padding) === "undefined" || padding === null ? padding = 2 : padding;

    while (hex.length < padding) {
        hex = "0" + hex;
    }
    
    while (hex.length > 0) {
        littleEndian = hex.substring(0, 2) + littleEndian;
        hex = hex.substring(2, hex.length);
    }
    return littleEndian;
}



function BmsLion_toggleSettingsItem(elem) {
  if (elem.childNodes[0].innerHTML == "1") {
    elem.childNodes[0].innerHTML = "0";
  } else {
    elem.childNodes[0].innerHTML = "1";    
  }
  BmsLion_settingsRefresh();
}

function BmsLion_toggleSettingsModule(str, module) {
  var elem;
  for (var cell = 0; cell < 18; cell++) {
    elem = document.getElementById(str+module+"cs"+cell);
    if (elem.innerHTML == '0') {
      elem.innerHTML = "1";    
    } else {
      elem.innerHTML = "0";
    }
  }
  BmsLion_settingsRefresh();
}

function BmsLion_setSettingsAll() {
  for (var module = 0; module < 16; module++) {
    for (var cell = 0; cell < 18; cell++) {
      document.getElementById("vm"+module+"cs"+cell).innerHTML = "1";
      document.getElementById("tm"+module+"cs"+cell).innerHTML = "1";
    }
  }
  BmsLion_settingsRefresh();
}

function BmsLion_clearSettingsAll() {
  for (var module = 0; module < 16; module++) {
    for (var cell = 0; cell < 18; cell++) {
      document.getElementById("vm"+module+"cs"+cell).innerHTML = "0";
      document.getElementById("tm"+module+"cs"+cell).innerHTML = "0";
    }
  }
  BmsLion_settingsRefresh();
}
