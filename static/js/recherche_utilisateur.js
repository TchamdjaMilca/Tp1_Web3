let ctrlUser = null;

const rechercheUser = document.getElementById("recherche-user");
const listeUsers = document.getElementById("liste-users");
const chargementUsers = document.getElementById("chargement-users");
const erreurUsers = document.getElementById("erreur-users");

function chargerHistorique() {
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

    if (!hist.includes(email)) {
        hist.push(email);
        localStorage.setItem("rechercheUsers", JSON.stringify(hist));
    }
}

async function rechercherUtilisateur() {
    const email = rechercheUser.value.trim();

    listeUsers.textContent = "";
    chargementUsers.classList.add("masquer");
    erreurUsers.classList.add("masquer");

    if (email.length < 4) return;

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

        li.addEventListener("click", () => {
            rechercheUser.value = user.courriel;
            rechercherUtilisateur();
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

document.addEventListener("DOMContentLoaded", function () {

    const tbody = document.querySelector("tbody");
    if (!tbody) return;

    tbody.addEventListener("click", function (e) {

        if (e.target.matches(".form-supprimer-utilisateur button")) {

            e.preventDefault(); 

            const form = e.target.closest("form");
            const tr = form.closest("tr");

            if (!confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) return;

            fetch(form.action, {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
                .then(res => res.json())
                .then(data => {

                    if (data.succes) {
                        tr.remove(); 
                        return;       
                    }

                    alert(data.message || "Erreur lors de la suppression.");
                })
                .catch(err => {
                    console.error("Erreur AJAX:", err);
                    alert("Erreur lors de la suppression.");
                });
        }
    });
});
