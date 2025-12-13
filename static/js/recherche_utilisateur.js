"use strict";

let ctrlUser = null;

const rechercheUser = document.getElementById("recherche-user");
const listeUsers = document.getElementById("liste-users");
const chargementUsers = document.getElementById("chargement-users");
const erreurUsers = document.getElementById("erreur-users");

listeUsers.innerHTML = "";
function chargerHistorique() {
    listeUsers.textContent = "";
    const hist = JSON.parse(localStorage.getItem("rechercheUsers") || "[]");

    for (const email of hist) {
        const li = document.createElement("li");
        li.textContent = email;
        li.classList.add("historique");
        li.addEventListener("click", () => {
            rechercheUser.value = email;
            rechercherUtilisateur();
        });
        listeUsers.append(li);
    }
}

function sauvegarderRecherche(email) {
    let hist = JSON.parse(localStorage.getItem("rechercheUsers") || "[]");
    hist = hist.filter(item => item !== email);
    hist.push(email);
    if (hist.length > 5) {
        hist.shift();
    }
    localStorage.setItem("rechercheUsers", JSON.stringify(hist));
}



async function rechercherUtilisateur() {
    const email = rechercheUser.value.trim();

    listeUsers.textContent = "";
    chargementUsers.classList.add("masquer");
    erreurUsers.classList.add("masquer");

    if (email.length < 3) return;

    chargementUsers.classList.remove("masquer");


    if (ctrlUser !== null) {
        ctrlUser.abort();
    }
    ctrlUser = new AbortController();

    try {
        const resultats = await envoyerRequeteAjax(
            "/api/utilisateurs",
            "GET",
            { email: email },
            ctrlUser
        );

        afficherResultatsUsers(resultats);
        sauvegarderRecherche(email);

    } catch (err) {
        afficherErreurUsers(err);
    }
}

function afficherResultatsUsers(resultats) {
    listeUsers.textContent = "";

    for (const user of resultats) {
        const li = document.createElement("li");
        li.textContent = `${user.courriel} (${user.nom})`;

        li.addEventListener("click", async () => {
            rechercheUser.value = user.courriel;

            listeUsers.textContent = "";

            const liUnique = document.createElement("li");
            liUnique.textContent = `${user.courriel} (${user.nom})`;
            listeUsers.append(liUnique);

            sauvegarderRecherche(user.courriel);
        });


        listeUsers.append(li);
    }

    chargementUsers.classList.add("masquer");
    ctrlUser = null;
}

function afficherErreurUsers(err) {
    if (err.name !== "AbortError") {
        erreurUsers.textContent = "Erreur AJAX";
    }
    chargementUsers.classList.add("masquer");
}


rechercheUser.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        rechercherUtilisateur();
    }
});

window.addEventListener("load", () => {
    chargerHistorique();
    rechercheUser.addEventListener("input", rechercherUtilisateur);
});


document.addEventListener("DOMContentLoaded", () => {
    const tbody = document.querySelector("tbody");
    if (!tbody) return;

    tbody.addEventListener("click", async function (e) {

        if (!e.target.matches(".form-supprimer-utilisateur button")) return;

        e.preventDefault();

        const form = e.target.closest("form");
        const tr = form.closest("tr");

        if (!confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) return;

        try {

            const data = await envoyerRequeteAjax(
                form.action,
                "POST",
                {},
            );

            if (data.succes) {
                tr.remove();
                return;
            }

            alert(data.message || "Erreur lors de la suppression.");

        } catch (err) {
            console.error("Erreur AJAX:", err);
            alert("Erreur lors de la suppression.");
        }
    });
});
