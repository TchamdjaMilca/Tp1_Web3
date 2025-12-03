"use strict";

let controleurRequete = null;
let listeServices = null;
let recherche = null;

async function rechercher() {
    const texte = recherche.value.trim();

    if (texte.length < 3) {
        listeServices.innerHTML = "<li>Tape au moins 3 caractères</li>";
        if (controleurRequete) controleurRequete.abort();
        return;
    }

    controleurRequete = new AbortController();

    const resultats = await envoyerRequeteAjax(
        "/services/api/recherche",
        "GET",
        { "mots-cles": texte },
        controleurRequete
    );

    console.log(resultats);

    listeServices.innerHTML = "";

    for (const service of resultats) {
        const li = document.createElement("li");
        li.textContent = service.titre;
        li.classList.add("list-group-item", "list-group-item-action");
        listeServices.appendChild(li);
    }
}

function initialisation() {

    listeServices = document.getElementById("lstServices");
    recherche = document.getElementById("recherche");
    recherche.addEventListener("input", rechercher);
}

window.addEventListener("load", initialisation);
