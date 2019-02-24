function Get(yourUrl){
    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var Httpreq = new XMLHttpRequest(); // a new request
    Httpreq.open("GET", yourUrl, false);
    Httpreq.send(null);
    return Httpreq.responseText;
}

const URL="http://api.mygasfeed.com/stations/radius/29.760427/-95.369804/1/reg/price/3apmnfw3ul.json?callback=?"
var data = Get(URL);
// var json = JSON.parse(data.substring(2, data.length - 1))
console.log(data);
