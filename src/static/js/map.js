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
function showRegionInfo(e) {
    var properties = e.target.feature.properties;
    document.getElementById('region-name').textContent = properties.nom ? properties.nom : properties.raison_sociale;
    document.getElementById('region-nombre-installations').textContent = properties.num_installations ? "Nombre d'installations : " + f(properties.num_installations) : '';
    document.getElementById('region-quantite-autorisee').textContent = "Quantité Autorisée : " + f(properties.quantite_autorisee) + "t";
    document.getElementById('region-quantite-traitee').textContent = "Quantité Traitée : " + f(properties.quantite_traitee) + "t";
    document.getElementById('region-ratio-traitement').textContent = "Quantité consommée : " + f(properties.quantite_traitee * 100 / properties.quantite_autorisee) + "%";
    // Afficher la div
    document.getElementById('region-info').style.display = 'block';
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
function clickOnPolygonHandler(e) {
    zoomToPolygon(e);
    showRegionInfo(e);
    styleSelected(e);
}

function onEachPolygonFeature(feature, layer) {
    layer.on({
        click: clickOnPolygonHandler
    });

}

function clickOnPointHandler(e) {
    zoomToPoint(e);
    showRegionInfo(e);
}

function onEachPointFeature(feature, layer) {
    layer.on({
        click: clickOnPointHandler
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
            onEachFeature: onEachPolygonFeature
        })
    geojsonDepartements = L.geoJSON(selectedData["departements"],
        {
            style: stylePolygon,
            onEachFeature: onEachPolygonFeature
        });
    geojsonInstallations = L.geoJson(selectedData["installations"],
        {
            pointToLayer: stylePoint,
            onEachFeature: onEachPointFeature
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
    var quantite_traitee = feature.properties.quantite_traitee;
    var quantite_autorisee = feature.properties.quantite_autorisee;

    var ratio = quantite_traitee / quantite_autorisee;

    // Calcul de la couleur
    var fillColor;
    var fillOpacity;
    if (ratio == null) {
        fillColor = white;
        fillOpacity = 0.6
    } else if (ratio > 1) {
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