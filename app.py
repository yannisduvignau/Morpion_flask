from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Plateau initial vide
plateau = [[" " for _ in range(3)] for _ in range(3)]

# Ajoutez les scores globaux
scores = {"X": 0, "O": 0, "Match nul": 0}


# Réinitialise le plateau
def reinitialiser_plateau():
    global plateau
    plateau = [[" " for _ in range(3)] for _ in range(3)]


# Vérifie s'il y a un gagnant
def verifier_gagnant(plateau):
    for ligne in plateau:
        if ligne[0] == ligne[1] == ligne[2] and ligne[0] != " ":
            return ligne[0]
    for col in range(3):
        if plateau[0][col] == plateau[1][col] == plateau[2][col] and plateau[0][col] != " ":
            return plateau[0][col]
    if plateau[0][0] == plateau[1][1] == plateau[2][2] and plateau[0][0] != " ":
        return plateau[0][0]
    if plateau[0][2] == plateau[1][1] == plateau[2][0] and plateau[0][2] != " ":
        return plateau[0][2]
    return None


# Vérifie si le plateau est plein
def plateau_plein(plateau):
    return all(cell != " " for ligne in plateau for cell in ligne)


# Algorithme Minimax
def minimax(plateau, is_maximizing, joueur_ia, joueur_humain):
    gagnant = verifier_gagnant(plateau)
    if gagnant == joueur_ia:
        return 1
    elif gagnant == joueur_humain:
        return -1
    elif plateau_plein(plateau):
        return 0

    if is_maximizing:
        meilleur_score = -math.inf
        for i in range(3):
            for j in range(3):
                if plateau[i][j] == " ":
                    plateau[i][j] = joueur_ia
                    score = minimax(plateau, False, joueur_ia, joueur_humain)
                    plateau[i][j] = " "
                    meilleur_score = max(meilleur_score, score)
        return meilleur_score
    else:
        meilleur_score = math.inf
        for i in range(3):
            for j in range(3):
                if plateau[i][j] == " ":
                    plateau[i][j] = joueur_humain
                    score = minimax(plateau, True, joueur_ia, joueur_humain)
                    plateau[i][j] = " "
                    meilleur_score = min(meilleur_score, score)
        return meilleur_score


# IA choisit le meilleur mouvement
def meilleur_mouvement(plateau, joueur_ia, joueur_humain):
    meilleur_score = -math.inf
    coup = None
    for i in range(3):
        for j in range(3):
            if plateau[i][j] == " ":
                plateau[i][j] = joueur_ia
                score = minimax(plateau, False, joueur_ia, joueur_humain)
                plateau[i][j] = " "
                if score > meilleur_score:
                    meilleur_score = score
                    coup = (i, j)
    return coup


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/jouer', methods=['POST'])
def jouer():
    global plateau
    data = request.json
    x, y = data.get("x"), data.get("y")
    mode = data.get("mode")  # "ia" ou "joueur"
    joueur_humain = data.get("joueur", "X")
    joueur_ia = "O" if joueur_humain == "X" else "X"

    # Humain joue
    if plateau[x][y] == " ":
        plateau[x][y] = joueur_humain
    else:
        return jsonify({"error": "Case déjà occupée"})

    # Vérifie si humain a gagné
    gagnant = verifier_gagnant(plateau)
    if gagnant:
        scores[gagnant] += 1
        return jsonify({"gagnant": gagnant, "plateau": plateau, "scores": scores})

    # Vérifie si match nul
    if plateau_plein(plateau):
        scores["Match nul"] += 1
        return jsonify({"gagnant": "Match nul", "plateau": plateau, "scores": scores})

    # Tour de l'IA ou du joueur 2
    if mode == "ia":
        coup = meilleur_mouvement(plateau, joueur_ia, joueur_humain)
        if coup:
            plateau[coup[0]][coup[1]] = joueur_ia
    else:
        joueur_humain = "O" if joueur_humain == "X" else "X"

    # Vérifie si IA ou joueur 2 a gagné
    gagnant = verifier_gagnant(plateau)
    if gagnant:
        scores[gagnant] += 1
        return jsonify({"gagnant": gagnant, "plateau": plateau, "scores": scores})

    # Vérifie si match nul après le tour IA/joueur 2
    if plateau_plein(plateau):
        scores["Match nul"] += 1
        return jsonify({"gagnant": "Match nul", "plateau": plateau, "scores": scores})

    return jsonify({"plateau": plateau, "gagnant": None, "scores": scores})

@app.route("/scores", methods=["GET"])
def obtenir_scores():
    """Retourne les scores actuels."""
    return jsonify(scores)

@app.route('/reinitialiser', methods=['POST'])
def reinitialiser():
    """Réinitialise le plateau sans modifier les scores."""
    global plateau
    plateau = [[" " for _ in range(3)] for _ in range(3)]
    return jsonify({"plateau": plateau})

@app.route('/reinitialiser_scores', methods=['POST'])
def reinitialiser_scores():
    """Réinitialise les scores."""
    global scores
    scores = {"X": 0, "O": 0, "Match nul": 0}
    return jsonify({"message": "Scores réinitialisés", "scores": scores})



if __name__ == "__main__":
    app.run(debug=True)
