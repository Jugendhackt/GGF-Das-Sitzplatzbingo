function showTrainInfo(result) {
    let counter = 0, reihen = 12;
    result.utilization.forEach(function (element) {
        let k = parseInt(element.wagonPosition);

        let gesamt = element.capacitySeatsFirst + element.capacitySeatsSecond;
        let reserviert = element.seatReservationsFirst + element.seatReservationsSecond;
        let auslastung = Math.round(((reserviert / gesamt) * 100));

        let hinzu2 = "<div class='wagen' id='wagen" + k + "'> Auslastung: " + auslastung + "%</div>";
        document.getElementById("ice").innerHTML += hinzu2;
        for (let j = 1; j <= reihen; j++) {
            let hinzu1 = "<div id='" + k + "reihe" + j + "'></div>";
            document.getElementById("wagen" + k).innerHTML += hinzu1;
            for (let i = 0; i <= 4; i++) {
                let hinzu = '';
                if (i === 2) {
                    hinzu = "<div class='zwischenraum'></div>";
                } else {
                    counter += 1;
                    if (Math.random() * 100 < auslastung) {
                        hinzu = "<div id='sitz" + counter + "' class='sitz' style='background: #333333'>" + ((counter - 1) % (4 * reihen) + 1) + "</div>";
                    } else {
                        hinzu = "<div id='sitz" + counter + "' class='sitz'>" + ((counter - 1) % (4 * reihen) + 1) + "</div>";
                    }

                }
                document.getElementById(k + "reihe" + j).innerHTML += hinzu;
            }
        }
    });
}

$("button#search").on("click", function (event) {
    event.preventDefault();

    const startort = encodeURIComponent($('input#startort').val()),
        zugnummer = $('input#zugnummer').val(),
        datum = $('input#datum').val();

    $.ajax({
        url: "https://ggf-backend.margau.me/seats/" + zugnummer + "/" + datum + "/" + startort,
        type: "GET",
        crossDomain: true,
        success: function (result) {
            showTrainInfo(result);
        },
        error: function (result) {
            let error;
            if ('responseText' in result) {
                error = JSON.parse(result.responseText).error;
            } else {
                error = 'Unbekannter Fehler'
            }
            alert('Fehler: ' + error);
        }
    });
});