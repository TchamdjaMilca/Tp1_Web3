const inputDate = document.getElementById("date_heure_reservation");
const btn = document.querySelector("button[type='submit']");

const retro = document.createElement("div");
retro.classList.add("mt-2");
inputDate.parentNode.appendChild(retro);

let ctrl = null;

inputDate.addEventListener("input", async () => {
    const date = inputDate.value;

    retro.textContent = "";
    btn.disabled = true;

    if (!date) return;

    if (ctrl !== null) ctrl.abort();
    ctrl = new AbortController();

    try {
        const rep = await fetch(`/reservation/verifier_disponibilite/${idService}?date_heure=${encodeURIComponent(date)}`, {
            method: "GET",
            signal: ctrl.signal
        });

        const data = await rep.json();

        if (!data.disponible) {
            retro.textContent = " Créneau non disponible";
            retro.className = "text-danger mt-2";
            btn.disabled = true;
        } else {
            retro.textContent = " Disponible";
            retro.className = "text-success mt-2";
            btn.disabled = false;
        }

    } catch (err) {
        if (err.name !== "AbortError") {
            retro.textContent = "Erreur de vérification";
            retro.className = "text-danger mt-2";
            btn.disabled = true;
        }
    }
});
