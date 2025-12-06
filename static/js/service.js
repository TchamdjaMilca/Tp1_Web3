/**
 * Script pour l'affichage de suggestion de recherche
 */

"use strict"

let divSuggestions = null;
let rechercherInput = null;
let controleur = null;
let debut = 0;
const limite = 6;
let finished = false;
let loading = false;


/**
 * Appelée lors d'un clic dans la fenêtre.
 */
function gererClicFenetre(evenement) {
    const clicDansDivision = divSuggestions.contains(evenement.target);
    console.log("Clic dans la zone cliquable ? " + clicDansDivision)
    if (!clicDansDivision) {
        divSuggestions.replaceChildren()
        divSuggestions.classList.remove("afficher")
        document.removeEventListener("click", gererClicFenetre)
    }
}


/**
 * Pour demander les suggestions au site web.
 *
 * On devrait procéder par AJAX pour récupérer les suggestions, mais
 * elles sont "hard-codés" pour la démo.
 */
async function afficherSuggestions() {

    divSuggestions.replaceChildren();
    divSuggestions.classList.add("afficher");

    const ul = document.createElement("ul");
    divSuggestions.append(ul);

    const motCle = rechercherInput.value;

    if (motCle.length < 3) {
        const li = document.createElement("li");
        li.textContent = "Tape au moins 3 caractères";
        li.style.color = "gray";
        ul.append(li);

    }
    else {

        if (controleur)
            controleur.abort();
        controleur = new AbortController();

        const resultats = await envoyerRequeteAjax(
            `/api/recherche`,
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

        ul.addEventListener('click', function (e) {
            const id = e.target.dataset.id;

            if (id) {
                ajouterElementAuTableau(rechercherInput.value);

                // TODO: rediriger vers la page du service

            }


        });

    }


}


function getTableauFromLocalStorage() {
    let tableauEnregistre = localStorage.getItem('tableauLocal');
    // Si le tableau existe dans le localStorage, le parse en objet js (json) et le retourne, sinon retourne un tableau vide
    return tableauEnregistre ? JSON.parse(tableauEnregistre) : [];
}

function ajouterElementAuTableau(nouvelElement) {
    // Récupérer le tableau actuel depuis le localStorage
    let tableauActuel = getTableauFromLocalStorage();

    // Ajouter le nouvel élément au tableau
    // TODO : vérifier si l'élément n'existe pas déjà dans le tableau avant de l'ajouter
    if (!tableauActuel.includes(nouvelElement)) {


        tableauActuel.push(nouvelElement);
        if (tableauActuel.length > 5) {
            tableauActuel.shift();
        }
    }


    // Sauvegarder le tableau mis à jour dans le localStorage
    localStorage.setItem('tableauLocal', JSON.stringify(tableauActuel));
}

function afficherLocalStorage() {
    let tableau = getTableauFromLocalStorage()
    const ul = document.createElement("ul")

    divSuggestions.replaceChildren()
    divSuggestions.classList.add("afficher")
    divSuggestions.append(ul)

    for (const t of tableau) {
        const li = document.createElement("li")
        li.innerHTML = " " + t + ""
        ul.append(li)
    }

    ul.addEventListener('click', function (e) {
        rechercherInput.value = e.target.innerText;    // la valeur sélectionnée avec le clic de la souris
        afficherSuggestions();
        divSuggestions.innerHTML = ''; // Effacer la liste déroulante après la sélection
    })

}


async function supprimerService(e) {
    const id = e.currentTarget.value;

    if (controleur)
        controleur.abort();

    controleur = new AbortController();

    const reponse = await envoyerRequeteAjax(
        `/api/supprimer/${id}`,
        "DELETE"
    );

    if (reponse.succes) {
        let bloc = document.getElementById(id);
        bloc.remove();
    }
    else {
        let erreurSpan = document.getElementById("erreur");
        erreurSpan.textContent = "Impossible de supprimer le service car il a des réservations associées.";
    }
}

/**
 * Appelée lors de l'initialisation de la page
 */

function initialisation() {


    divSuggestions = document.getElementById("div-suggestions");
    rechercherInput = document.getElementById("service");


    rechercherInput.addEventListener("input", afficherSuggestions);
    rechercherInput.addEventListener("focus", afficherLocalStorage);


    let boutons = document.getElementsByClassName("btn-supprimer");
    for (let i = 0; i < boutons.length; i++) {
        boutons[i].addEventListener("click", supprimerService);
    }

    window.addEventListener("scroll", gererScroll);

}


window.addEventListener("load", initialisation)
