const menu = document.querySelector(".menu");
const plateauContainer = document.querySelector(".plateau-container");
const plateau = document.getElementById("plateau");
const message = document.getElementById("message");
const scores = document.getElementById("scores");
let modeDeJeu = null; // "ia" ou "joueur"
let jeuTerminé = false;
let joueurActuel = "X";

// Retour au choix de mode de jeu
async function retourMDJ() {
    // Réinitialise les scores côté backend
    await fetch("/reinitialiser_scores", { method: "POST" });
    
    // Réinitialise les scores côté frontend
    document.getElementById("score-x").textContent = "0";
    document.getElementById("score-o").textContent = "0";
    document.getElementById("score-nul").textContent = "0";

    // Affiche le menu principal et masque le plateau
    menu.classList.add("active");
    plateauContainer.classList.remove("active");
    scores.classList.remove("active");
}

// Affiche le menu ou le plateau
function choisirMode(mode) {
    modeDeJeu = mode;
    menu.classList.remove("active");
    plateauContainer.classList.add("active");
    scores.classList.add("active");
    reinitialiser();
}

// Afficher le plateau
function afficherPlateau(plateauData) {
    plateau.innerHTML = '';
    plateauData.forEach((ligne, i) => {
        ligne.forEach((cell, j) => {
            const div = document.createElement("div");
            div.className = `case ${cell !== " " ? "occupée" : ""}`;
            if (cell === "X") {
                div.innerHTML = '<span class="material-icons">close</span>'; // Croix
            } else if (cell === "O") {
                div.innerHTML = '<span class="material-icons">circle</span>'; // Cercle
            }
            if (!jeuTerminé && cell === " ") {
                div.onclick = () => jouer(i, j);
            }
            plateau.appendChild(div);
        });
    });
}

// Envoyer un coup
async function jouer(x, y) {
    if (jeuTerminé) return;

    const response = await fetch("/jouer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x, y, mode: modeDeJeu, joueur: joueurActuel }),
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
    } else {
        afficherPlateau(data.plateau);
        if (data.gagnant) {
            jeuTerminé = true;
            message.textContent = `Résultat : ${data.gagnant}`;
        } else if (modeDeJeu === "joueur") {
            joueurActuel = joueurActuel === "X" ? "O" : "X";
            message.textContent = `Tour du joueur : ${joueurActuel}`;
        } else {
            message.textContent = "Tour en cours...";
        }
        await mettreAJourScores(); // Mettre à jour les scores
    }
}

// Réinitialiser le jeu
async function reinitialiser() {
    jeuTerminé = false;
    joueurActuel = "X";
    message.textContent = "Tour en cours...";
    const response = await fetch("/reinitialiser", {
        method: "POST"
    });
    const data = await response.json();
    afficherPlateau(data.plateau);
}

async function mettreAJourScores() {
    const response = await fetch("/scores");
    const scores = await response.json();
    document.getElementById("score-x").textContent = scores.X || "0";
    document.getElementById("score-o").textContent = scores.O || "0";
    document.getElementById("score-nul").textContent = scores["Match nul"] || "0";
}

// Initialisation
menu.classList.add("active");
mettreAJourScores();
