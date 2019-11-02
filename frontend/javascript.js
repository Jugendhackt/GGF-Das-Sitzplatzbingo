var counter = 0;

var reihen = 12;
var waegen = 10;

for(var k = 1; k <= waegen; k++){
	var hinzu2 = "<div class='wagen' id='wagen" + k + "'></div>";
	document.getElementById("ice").innerHTML += hinzu2;
	for(var j = 1; j <= reihen; j++){
		var hinzu1 = "<div id='" + k + "reihe" + j + "'></div>";
		document.getElementById("wagen" + k).innerHTML += hinzu1;
		for(var i = 0; i <= 4; i++){
			if(i == 2){
				hinzu = "<div class='zwischenraum'></div>";
			}else{
				counter += 1;
				var hinzu = "<div id='sitz" + counter + "' class='sitz'>" + ((counter - 1) % (4 * reihen) + 1) + "</div>";
			}
			document.getElementById(k + "reihe" + j).innerHTML += hinzu;
		}
	}
}