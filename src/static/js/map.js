// Fonction pour charger les données GeoJSON
function loadGeoJSONData(url) {
    return fetch(url).then(function (response) {
        if (!response.ok) {
            throw new Error('Erreur réseau lors du chargement du GeoJSON');
        }
        return response.json();
    });
}

// Fonctions pour le zoom
function zoomToPolygon(e) {
    map.fitBounds(e.target.getBounds(), { padding: [100, 100] });
}

function zoomToPoint(e) {
    map.flyTo(e.target.getLatLng(), 9)
}

// D3.js
// Configuration de D3 pour le formatage des nombres
var locale = d3.formatLocale({
    decimal: ".",
    thousands: " ",
    grouping: [3],
    currency: ["", "€"]
});
var f = locale.format(",.0f");

// Échelle de couleur D3 pour les styles des régions/départements
var colorScale = d3.scaleSequential(d3.interpolateOranges);

// Affiche les informations d'une région/département/installation dans une div
function showRegionInfo(e, rubrique, featureType) {
    var properties = e.target.feature.properties;

    var regionInfoDiv = document.getElementById("region-info");
    regionInfoDiv.replaceChildren();

    var processedQuantity_key = "moyenne_quantite_journaliere_traitee";
    var unit = "t/j";
    var processedQuantityPrefix = "Quantité journalière traitée en moyenne :";
    var usedQuantityPrefix = "Quantité journalière consommée en moyenne :";
    if (rubrique == "2760-1") {
        processedQuantity_key = "cumul_quantite_traitee";
        unit = "t/an";
        processedQuantityPrefix = "Quantité traitée en cummulé :"
        usedQuantityPrefix = "Quantité consommée sur l'année :"
    }

    if (featureType == "installation") {
        e = document.createElement("h2")
        e.textContent = properties.raison_sociale
        regionInfoDiv.append(e)

        e = document.createElement("p")
        e.textContent = `Code AIOT : ${properties.code_aiot}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        e.textContent = `SIRET : ${properties.siret}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        var authorizedQuantity = f(properties.quantite_autorisee)
        e.textContent = `Quantité autorisée : ${authorizedQuantity} ${unit}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        var processedQuantity = properties[processedQuantity_key]
        e.textContent = `${processedQuantityPrefix} ${f(processedQuantity)} ${unit}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        var usedQuantity = ""
        if (authorizedQuantity) {
            var usedQuantity = 100 * processedQuantity / properties.quantite_autorisee
        }
        e.textContent = `${usedQuantityPrefix} ${f(usedQuantity)}%`
        regionInfoDiv.append(e)
    } else {
        e = document.createElement("h2")
        e.textContent = properties.nom
        regionInfoDiv.append(e)

        e = document.createElement("p")
        e.textContent = `Nombre d'installations : ${properties.nombre_installations}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        e.textContent = `Quantité autorisée : ${properties.quantite_autorisee} ${unit}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        var processedQuantity = properties[processedQuantity_key]
        e.textContent = `${processedQuantityPrefix} ${f(processedQuantity)} ${unit}`
        regionInfoDiv.append(e)

        e = document.createElement("p")
        var usedQuantity = 100 * processedQuantity / properties.quantite_autorisee
        e.textContent = `${usedQuantityPrefix} ${f(usedQuantity)}%`
        regionInfoDiv.append(e)
    }

    idDivGraph = "graph"
    Plotly.purge(idDivGraph);

    if (properties.graph) {
        var plotData = JSON.parse(properties.graph)
        Plotly.newPlot(
            idDivGraph,
            plotData.data,
            plotData.layout);
    }

}


// Mettre en surbrillance la région ou le département sélectionné
function styleSelected(e) {

    if (currentSelectedLayer) {
        currentSelectedLayer.setStyle({
            color: '#2f3640',
            weight: 1,
        });
    }

    currentSelectedLayer = e.target;

    e.target.setStyle({
        color: '#2c3e50',
        weight: 4,
        opacity: 1,
    })
}

// Gestionnaires d'événements pour interagir avec les polygones et les points
function clickOnPolygonHandler(e, rubrique) {
    zoomToPolygon(e);
    showRegionInfo(e, rubrique, "region");
    styleSelected(e);
}

function onEachPolygonFeature(feature, layer, rubrique) {
    layer.on({
        click: (e) => { clickOnPolygonHandler(e, rubrique) }
    });

}

function clickOnPointHandler(e, rubrique) {
    zoomToPoint(e);
    showRegionInfo(e, rubrique, "installation");
}

function onEachPointFeature(feature, layer, rubrique) {
    layer.on({
        click: (e) => { clickOnPointHandler(e, rubrique) }
    });

}


// Calcul du ratio de consommation
function getPercentage(quantite_traitee, quantite_autorisee) {
    if (quantite_autorisee == null) { return 'Pas de quantité autorisée.' }
    if (quantite_traitee == null) { return 'Pas de quantité traitée.' }
    return ((quantite_traitee / quantite_autorisee) * 100).toFixed(2) + '%'; // Formaté en pourcentage, avec deux décimales
}

// Ajoute ou enlève une couche
function setLayer(layerName) {
    if (currentLayer) {
        map.removeLayer(currentLayer);
    }

    if (layerName === 'regions') {
        currentLayer = geojsonRegions;
    } else if (layerName === 'departements') {
        currentLayer = geojsonDepartements;
    }
    else {
        currentLayer = null;
    }

    if (currentLayer) {
        map.addLayer(currentLayer);
    }
}

// Ajoute ou enlève la couche contenant les installations
function setInstallations() {
    if (installationsToggled) {
        map.addLayer(geojsonInstallations);
    } else {
        map.removeLayer(geojsonInstallations);
    }
}

// Crée et configure les couches GeoJSON en fonction des données sélectionnées
function initMapForRubrique(icpe_data, rubrique) {

    // Si les couches existent déjà sur la carte, il faut les retirer
    if (geojsonRegions) map.removeLayer(geojsonRegions);
    if (geojsonDepartements) map.removeLayer(geojsonDepartements);
    if (geojsonInstallations) map.removeLayer(geojsonInstallations);

    selectedData = icpe_data[rubrique]

    geojsonRegions = L.geoJSON(selectedData["regions"],
        {
            style: stylePolygon,
            onEachFeature: (feature, layer) => { onEachPolygonFeature(feature, layer, rubrique) }
        })
    geojsonDepartements = L.geoJSON(selectedData["departements"],
        {
            style: stylePolygon,
            onEachFeature: (feature, layer) => { onEachPolygonFeature(feature, layer, rubrique) }
        });
    geojsonInstallations = L.geoJson(selectedData["installations"],
        {
            pointToLayer: stylePoint,
            onEachFeature: (feature, layer) => { onEachPointFeature(feature, layer, rubrique) }
        });

    setLayer(selectedLayer);
}

// Gestionnaire d'événements pour le sélecteur de couche
document.getElementById('layer-select').addEventListener('change', function (e) {

    selectedLayer = e.target.value;
    setLayer(selectedLayer)

});

// Gestionnaire d'événements pour le sélecteur de rubrique
document.getElementById('rubrique-select').addEventListener('change', function (e) {
    selectedRubrique = e.target.value;
    initMapForRubrique(icpeData, e.target.value);
    setInstallations()

});

// Gestionnaire d'événements pour le bouton toggle des installations
document.getElementById('toggle-installations').addEventListener('change', function (e) {
    installationsToggled = e.target.checked;
    setInstallations()


});



// Styles pour les régions/départements
function stylePolygon(feature) {
    // Extract the relevant properties
    var quantite_traitee = feature.properties.cumul_quantite_traitee ? feature.properties.cumul_quantite_traitee : feature.properties.moyenne_quantite_journaliere_traitee;
    var quantite_autorisee = feature.properties.quantite_autorisee;

    var ratio = quantite_traitee / quantite_autorisee;

    // Calcul de la couleur
    var fillColor;
    var fillOpacity;
    if ((ratio == null) || (!Number.isFinite(ratio))) {
        ratio = NaN
    }

    if (ratio > 1) {
        fillColor = 'url(#stripes)';
        fillOpacity = 1;
    } else {
        fillColor = colorScale(ratio);
        fillOpacity = 0.6;
    }

    return {
        fillColor: fillColor,
        weight: 1,
        opacity: 0.6,
        color: '#2f3640', // couleur des bordures
        fillOpacity: 0.6
    };
}


// Style pour les points des installations (à modifier)
function stylePoint(geoJsonPoint, latlng) {

    return L.marker(latlng);
}