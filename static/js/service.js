"use strict";

let divSuggestions = null;
let rechercherInput = null;
let controleur = null;

let visibles = 6;
const increment = 3;



function gererClicFenetre(evenement) {
    const clicDansDivision = divSuggestions.contains(evenement.target);
    console.log("Clic dans la zone cliquable ? " + clicDansDivision)
    if (!clicDansDivision) {
        divSuggestions.replaceChildren()
        divSuggestions.classList.remove("afficher")
        document.removeEventListener("click", gererClicFenetre)
    }
}


async function afficherSuggestions() {

    divSuggestions.replaceChildren();
    divSuggestions.classList.add("afficher");

    const ul = document.createElement("ul");
    divSuggestions.append(ul);

    const motCle = rechercherInput.value.trim();

    if (motCle.length < 3) {
        const li = document.createElement("li");
        li.textContent = "Tape au moins 3 caractères";
        li.style.color = "gray";
        ul.append(li);
        return;
    }

    if (controleur) controleur.abort();
    controleur = new AbortController();

    const resultats = await envoyerRequeteAjax(
        "/api/recherche",
        "GET",
        { "mots-cles": motCle },
        controleur
    );

    for (const service of resultats) {
        const li = document.createElement("li");
        li.textContent = service.titre;
        li.dataset.id = service.id_service;
        ul.append(li);
    }

    ul.addEventListener("click", (e) => {
        const id = e.target.dataset.id;
        if (id) {
            ajouterElementAuTableau(rechercherInput.value);
            window.location.href = `/services/details/${id}`;
        }
    });

    document.addEventListener("click", gererClicFenetre);
}


function getTableauFromLocalStorage() {
    const data = localStorage.getItem("tableauLocal");
    return data ? JSON.parse(data) : [];
}

function ajouterElementAuTableau(nouvelElement) {
    let tableau = getTableauFromLocalStorage();

    if (!tableau.includes(nouvelElement)) {
        tableau.push(nouvelElement);
        if (tableau.length > 5) tableau.shift();
    }

    localStorage.setItem("tableauLocal", JSON.stringify(tableau));
}

function afficherLocalStorage() {
    const tableau = getTableauFromLocalStorage();
    const ul = document.createElement("ul");

    divSuggestions.replaceChildren();
    divSuggestions.classList.add("afficher");
    divSuggestions.append(ul);

    for (const t of tableau) {
        const li = document.createElement("li");
        li.textContent = t;
        ul.append(li);
    }

    ul.addEventListener("click", (e) => {
        rechercherInput.value = e.target.innerText;
        afficherSuggestions();
        divSuggestions.innerHTML = "";
    });
}



async function supprimerService(e) {
    const id = e.currentTarget.value;

    const reponse = await envoyerRequeteAjax(
        `/api/supprimer/${id}`,
        "DELETE"
    );

    if (reponse.succes) {
        const bloc = document.getElementById(id);
        if (bloc) bloc.remove();
    } else {
        document.getElementById("erreur").textContent =
            "Impossible de supprimer le service car il a des réservations associées.";
    }
}

function afficherServices() {
    const services = document.querySelectorAll(".service-item");

    for (let i = 0; i < services.length; i++) {
        if (i < visibles) {
            services[i].classList.remove("d-none");
        } else {
            services[i].classList.add("d-none");
        }
    }
    gererDefilement();
}


function gererDefilement() {
     if ((window.innerHeight + window.scrollY) >= 0.95 * document.body.offsetHeight) {
        visibles += increment;
        afficherServices();
    }
}


function initialisation() {

    divSuggestions = document.getElementById("div-suggestions");
    rechercherInput = document.getElementById("service");

    rechercherInput.addEventListener("input", afficherSuggestions);
    rechercherInput.addEventListener("focus", afficherLocalStorage);

    const boutons = document.getElementsByClassName("btn-supprimer");
    for (let i = 0; i < boutons.length; i++) {
        boutons[i].addEventListener("click", supprimerService);
    }

     const services = document.querySelectorAll(".service-item");
    for (let i = 0; i < services.length; i++) {
        services[i].classList.add("d-none");
    }
    afficherServices();

    window.addEventListener("scroll", gererDefilement);
}

window.addEventListener("load", initialisation);
