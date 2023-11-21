function populateRubriquesTable(installationRubriques) {
    tTableElement = document.querySelector("#installation-rubriques-table table");
    tTableElement.removeChild(tTableElement.lastChild)

    tBodyElement = document.createElement("tbody");
    installationRubriques.forEach((element) => {
        trElement = document.createElement("tr");

        ["rubrique", "nature", "quantite_autorisee", "unite"].forEach((e) => {
            let tdElement = document.createElement("td");
            tdElement.innerText = element[e];;
            trElement.appendChild(tdElement)
        });


        tBodyElement.appendChild(trElement);
    });



    tTableElement.appendChild(tBodyElement);

    tDivTableElement = document.querySelector("#installation-rubriques-table");
    tDivTableElement.style.display = "unset";
}

function populateInstallationInfos(installationData) {

    installationNameDiv = document.getElementById("installation-name");
    installationNameDiv.innerHTML = installationData.raison_sociale;

    installationAddressDiv = document.getElementById("installation-address");
    installationAddressDiv.querySelectorAll('*').forEach(n => n.remove());

    address1Div = document.createElement("div");
    address1Div.innerText = installationData.adresse1 ?? "";
    installationAddressDiv.appendChild(address1Div);
    ;
    address2Div = document.createElement("div");
    address2Div.innerText = installationData.adresse2 ?? "";
    installationAddressDiv.appendChild(address2Div);

    cpCommuneDiv = document.createElement("div");
    cpCommuneDiv.innerText = `${installationData.code_postal ?? ""} ${installationData.commune ?? ""}`;
    installationAddressDiv.appendChild(cpCommuneDiv);

    installationInfoDiv = document.getElementById("installation-infos")
    installationInfoDiv.style.display = "inherit";

}

function populateGraph2770(installation2770Data) {
    graphesContainerDiv = document.getElementById("#graphes");
    graphesContainerDiv.querySelectorAll('*').forEach(n => n.remove());

    if (installation2770Data !== null) {
        graphDiv = document.createElement("div");

        x = installation2770Data.map(a => a.day_of_processing);
        y = installation2770Data.map(a => a.quantite_traitee);




        data = [{
            type: "scatter",
            x: x,
            y: y,

        }];

        layout = {
            margin: { t: 0 }
        }
        Plotly.newPlot(graphDiv, data, layout);




        graphesContainerDiv.appendChild(graphDiv);
        graphesContainerDiv.style.display = "inherit";
    }

}

function onMarkerClick(e, installationData) {


    populateInstallationInfos(installationData);

    populateRubriquesTable(JSON.parse(installationData.rubriques_json));


    populateGraph2770(JSON.parse(installationData.stats_2770))

}

var map = L.map('map').setView([48.2226778, 3.7493862], 4);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

fetch('icpe-list/2023').then(response => {
    // Check if the response status is OK (200)
    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
})
    .then(data => {

        var data = data
        var markers = L.markerClusterGroup();


        data.forEach((element) => {
            markers.addLayer(
                L.marker(
                    [element.latitude, element.longitude],
                    { title: element.raison_sociale },
                ).bindPopup(`${element.raison_sociale}`).on('click', e => {
                    onMarkerClick(e, element)
                })
            );
        });
        map.addLayer(markers);
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });