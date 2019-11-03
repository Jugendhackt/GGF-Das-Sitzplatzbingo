function showTrainInfo(result) {
    let counter = 0, reihen = 12;
    document.getElementById("ice").innerHTML = '';
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

function showDirectCheck(result, waggon, sitz) {
    result.utilization.forEach(function (element) {
        if (element.wagonNumber === waggon) {
            const sitze = element.reservedSeats.map(seat => parseInt(seat, 10).toString()),
                sitzReserviertText = sitze.indexOf(sitz) > -1 ? '' : 'nicht ';
            document.getElementById("ice").innerHTML = '<h3>Dein Platz ist ' + sitzReserviertText + 'reserviert.</h3>';
        }
    });
}

$("button").on("click", function (event) {
    const buttonId = event.target.id;
    if (buttonId !== 'search' && buttonId !== 'direktcheck') {
        return;
    }

    event.preventDefault();

    const startort = encodeURIComponent($('input#startort').val()),
        zugnummer = $('input#zugnummer').val().replace(/\s/g, ''),
        datum = $('input#datum').val();

    $.ajax({
        url: "https://ggf-backend.margau.me/seats/" + zugnummer + "/" + datum + "/" + startort,
        type: "GET",
        crossDomain: true,
        success: function (result) {
            if (buttonId === 'search') {
                showTrainInfo(result);
            } else if (buttonId === 'direktcheck') {
                const waggon = $('input#waggon').val(),
                    sitz = $('input#sitz').val();
                showDirectCheck(result, waggon, sitz);
            }
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