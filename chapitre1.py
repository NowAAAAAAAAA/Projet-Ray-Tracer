import math

# --- 1. CONFIGURATION DE LA SCÈNE ---
# Dimensions de l'image (Canvas)
WIDTH = 400
HEIGHT = 400

# Le buffer est une liste simple qui contiendra nos pixels (R, G, B)
# On initialise tout en noir (0, 0, 0)
framebuffer = [(0, 0, 0)] * (WIDTH * HEIGHT)

# --- 2. FONCTIONS UTILITAIRES ---

def put_pixel(x, y, color):
    """
    Change la couleur d'un pixel aux coordonnées (x, y) de l'écran.
    L'écran a son origine (0,0) au centre pour simplifier les maths 3D,
    mais la liste informatique commence en haut à gauche. Il faut convertir.
    """
    # Conversion des coordonnées du "monde mathématique" (centre 0,0)
    # vers les coordonnées "informatiques" (haut-gauche 0,0)
    sx = int(WIDTH / 2 + x)
    sy = int(HEIGHT / 2 - y) # On inverse Y car en info, Y descend

    # Vérification pour ne pas dessiner en dehors de l'écran
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        index = sx + sy * WIDTH
        framebuffer[index] = color

def save_ppm_image(filename):
    """
    Sauvegarde le framebuffer dans un fichier image au format PPM (P3).
    C'est un format texte simple lisible par la plupart des visionneuses.
    """
    with open(filename, 'w') as f:
        # En-tête du fichier PPM
        f.write("P3\n")             # Magic number pour PPM couleur (texte)
        f.write(f"{WIDTH} {HEIGHT}\n") # Dimensions
        f.write("255\n")            # Valeur max des couleurs

        # Écriture des pixels
        for color in framebuffer:
            r, g, b = color
            # On s'assure que les valeurs sont entre 0 et 255
            r = max(0, min(255, int(r)))
            g = max(0, min(255, int(g)))
            b = max(0, min(255, int(b)))
            f.write(f"{r} {g} {b} \n")
    
    print(f"Image sauvegardée sous : {filename}")

# --- 3. BOUCLE PRINCIPALE (MAIN) ---

def main():
    print("Calcul de l'image en cours...")
    
    # Pour tester, on va dessiner un dégradé simple
    # On parcourt chaque pixel de l'écran mathématique
    # x va de -200 à +200, y va de -200 à +200
    left = -WIDTH // 2
    right = WIDTH // 2
    bottom = -HEIGHT // 2
    top = HEIGHT // 2

    for x in range(left, right):
        for y in range(bottom, top):
            # Couleur de test : Rouge basé sur X, Vert basé sur Y
            r = (x - left) * 255 / WIDTH
            g = (y - bottom) * 255 / HEIGHT
            b = 100 # Bleu fixe
            
            put_pixel(x, y, (r, g, b))

    # Sauvegarder le résultat
    save_ppm_image("test_gradient.ppm")

if __name__ == "__main__":
    main()