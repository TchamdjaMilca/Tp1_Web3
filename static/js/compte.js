const caracteres_interdits = /<|>/;
const regex_courriel = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
const regex_mot_de_passe = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;


function validerNom() {
    const nom = document.getElementById("nom").value.trim();
    const msg = document.getElementById("erreur-nom");
    msg.textContent = "";

    if (!nom) {
        msg.textContent = "Le nom ne peut pas être vide.";
    } else if (caracteres_interdits.test(nom)) {
        msg.textContent = "Le nom contient des caractères interdits (< >).";
    }
}

function validerPrenom() {
    const prenom = document.getElementById("prenom").value.trim();
    const msg = document.getElementById("erreur-prenom");
    msg.textContent = "";

    if (!prenom) {
        msg.textContent = "Le prénom ne peut pas être vide.";
    } else if (caracteres_interdits.test(prenom)) {
        msg.textContent = "Le prénom contient des caractères interdits (< >).";
    }
}

function validerCourriel() {
    const courriel = document.getElementById("courriel").value.trim();
    const msg = document.getElementById("erreur-courriel");
    msg.textContent = "";

    if (!courriel) {
        msg.textContent = "Le courriel ne peut pas être vide.";
    } else if (!regex_courriel.test(courriel)) {
        msg.textContent = "Le courriel n'est pas valide.";
    }
}

function validerMotDePasse() {
    const mdp = document.getElementById("mot_de_passe").value.trim();
    const msg = document.getElementById("erreur-motdepasse");
    msg.textContent = "";

    if (!mdp) {
        msg.textContent = "Le mot de passe ne peut pas être vide.";
    } else if (!regex_mot_de_passe.test(mdp)) {
        msg.textContent = "Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre.";
    }
}


function validerConfirmation() {
    const mdp = document.getElementById("mot_de_passe").value.trim();
    const conf = document.getElementById("confirmation_mot_de_passe").value.trim();
    const msg = document.getElementById("erreur-confirmation");
    msg.textContent = "";

    if (mdp !== conf) {
        msg.textContent = "La confirmation ne correspond pas.";
    }
}
function initialiserValidation() {
    document.getElementById("nom").addEventListener("input", validerNom);
    document.getElementById("prenom").addEventListener("input", validerPrenom);
    document.getElementById("courriel").addEventListener("input", validerCourriel);
    document.getElementById("mot_de_passe").addEventListener("input", validerMotDePasse);
    document.getElementById("confirmation_mot_de_passe").addEventListener("input", validerConfirmation);
}

window.addEventListener("load", initialiserValidation);