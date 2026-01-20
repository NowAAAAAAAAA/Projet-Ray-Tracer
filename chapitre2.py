import math

# ==========================================
# CHAPITRE 2 : BASIC RAYTRACING (GÉOMÉTRIE PURE)
# Objectif : Afficher la scène (Terre & Lune) sous forme de silhouettes colorées.
# Spécificité : Pas de lumière, pas de 3D apparente, juste des formes "plates".
# ==========================================

WIDTH = 400
HEIGHT = 400
framebuffer = [(0, 0, 0)] * (WIDTH * HEIGHT)

# --- 1. VECTEURS ---
class Vec3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __add__(self, v): return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)
    def __sub__(self, v): return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)
    def __mul__(self, s): return Vec3(self.x * s, self.y * s, self.z * s)
    
    def dot(self, v): return self.x * v.x + self.y * v.y + self.z * v.z
    
    def length(self): return math.sqrt(self.dot(self))

# --- 2. OBJETS ---
# Au Chapitre 2, une sphère n'a que sa géométrie et sa couleur de base.
# Pas de 'specular' (brillance) ni de 'reflective' (miroir).
class Sphere:
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color

# --- 3. MATHS D'INTERSECTION ---

def intersect_ray_sphere(origin, direction, sphere):
    """
    Résout l'équation quadratique pour savoir si le rayon touche la sphère.
    """
    oc = origin - sphere.center
    
    a = direction.dot(direction)
    b = 2 * oc.dot(direction)
    c = oc.dot(oc) - sphere.radius * sphere.radius

    discriminant = b*b - 4*a*c

    if discriminant < 0:
        return float('inf'), float('inf') # Pas d'intersection

    t1 = (-b + math.sqrt(discriminant)) / (2*a)
    t2 = (-b - math.sqrt(discriminant)) / (2*a)
    
    return t1, t2

def trace_ray(origin, direction, min_t, max_t, spheres):
    """
    Lance un rayon et retourne la couleur de l'objet le plus proche.
    Sans calcul de lumière, on retourne juste la couleur brute de l'objet.
    """
    closest_t = float('inf')
    closest_sphere = None

    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        
        # On cherche l'intersection valide la plus proche
        if min_t < t1 < max_t and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    if closest_sphere == None:
        return (0, 0, 0) # Fond noir
    
    # C'est ici la différence avec le Chap 3 :
    # On retourne directement la couleur, sans calculer d'angle avec une lumière.
    return closest_sphere.color

# --- 4. MOTEUR GRAPHIQUE ---

# Configuration Caméra
vw = 1
vh = 1
d = 1 

def canvas_to_viewport(x, y):
    return Vec3(x * vw / WIDTH, y * vh / HEIGHT, d)

def put_pixel(x, y, color):
    sx = int(WIDTH / 2 + x)
    sy = int(HEIGHT / 2 - y) - 1 # Correction d'index
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        framebuffer[sx + sy * WIDTH] = color

def save_ppm(filename):
    with open(filename, 'w') as f:
        f.write(f"P3\n{WIDTH} {HEIGHT}\n255\n")
        for c in framebuffer: f.write(f"{c[0]} {c[1]} {c[2]}\n")
    print(f"Image générée : {filename}")

# --- 5. MAIN ---

def main():
    print("Rendu Chapitre 2 (Formes plates aux positions finales)...")
    
    O = Vec3(0, 0, 0)

    # --- SCÈNE ALIGNÉE SUR LE PROJET FINAL ---
    # Positions identiques aux Chapitres 3, 4 et 5.
    
    # 1. LA TERRE (A gauche)
    # Vec3(-1.5, 0, 5)
    terre = Sphere(Vec3(-1.5, 0, 5), 1, (0, 0, 255))
    
    # 2. LA LUNE (Devant)
    # Vec3(-0.5, -0.6, 3)
    # Note : Comme elle est plus proche (z=3 vs z=5), 
    # le code va correctement la dessiner "par-dessus" la Terre.
    lune = Sphere(Vec3(-0.5, -0.6, 3), 0.4, (220, 220, 220))
    
    spheres = [terre, lune]

    # Boucle de rendu
    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            D = canvas_to_viewport(x, y)
            color = trace_ray(O, D, 1, float('inf'), spheres)
            put_pixel(x, y, color)

    save_ppm("chapitre2_formes.ppm")

if __name__ == "__main__":
    main()