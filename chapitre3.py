import math

# ==========================================
# CHAPITRE 3 : LUMIÈRE ET OMBRAGE (SCÈNE FLOTTANTE)
# Objectif : Rendu Terre & Lune identique au Chap 4, mais SANS ombres ni reflets
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
    
    def normalize(self):
        l = self.length()
        if l == 0: return Vec3(0,0,0)
        return Vec3(self.x / l, self.y / l, self.z / l)

# --- 2. OBJETS DE LA SCÈNE ---

class Sphere:
    def __init__(self, center, radius, color, specular):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular 
        # Note : Pas de 'reflective' ici, c'est propre au Chapitre 3

class Light:
    def __init__(self, l_type, intensity, position=None):
        self.type = l_type
        self.intensity = intensity
        self.position = position

# --- 3. MOTEUR PHYSIQUE (Lumière sans Ombres) ---

def compute_lighting(P, N, V, specular, lights):
    """
    Calcule l'éclairage local (Diffuse + Spéculaire).
    Spécificité Chap 3 : On ne vérifie PAS les ombres.
    """
    intensity = 0.0
    
    for light in lights:
        if light.type == 'ambient':
            intensity += light.intensity
        else:
            if light.type == 'point':
                L_vector = light.position - P
                L = L_vector 
            else:
                L = light.position 

            # Important : On normalise L pour les calculs d'angles
            L_dir = L.normalize()
            
            # 1. Diffuse (Lambert)
            n_dot_l = N.dot(L_dir)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (N.length() * L_dir.length())

            # 2. Spéculaire (Reflet brillant)
            if specular != -1:
                R = N * 2 * N.dot(L_dir) - L_dir
                r_dot_v = R.dot(V)
                if r_dot_v > 0:
                    intensity += light.intensity * pow(r_dot_v / (R.length() * V.length()), specular)

    return intensity

# --- 4. RAYTRACING ---

vw, vh, d = 1, 1, 1

def canvas_to_viewport(x, y):
    return Vec3(x * vw / WIDTH, y * vh / HEIGHT, d)

def intersect_ray_sphere(O, D, sphere):
    CO = O - sphere.center
    a = D.dot(D)
    b = 2 * CO.dot(D)
    c = CO.dot(CO) - sphere.radius**2
    delta = b*b - 4*a*c
    if delta < 0: return float('inf'), float('inf')
    t1 = (-b + math.sqrt(delta)) / (2*a)
    t2 = (-b - math.sqrt(delta)) / (2*a)
    return t1, t2

def trace_ray(O, D, min_t, max_t, spheres, lights):
    closest_t = float('inf')
    closest_sphere = None

    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(O, D, sphere)
        if min_t < t1 < max_t and t1 < closest_t:
            closest_t, closest_sphere = t1, sphere
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t, closest_sphere = t2, sphere

    if closest_sphere == None:
        return (0, 0, 0)

    # Calculs au point d'impact
    P = O + D * closest_t 
    N = (P - closest_sphere.center).normalize()
    V = D * -1 # Vecteur vue
    
    # Chapitre 3 : Juste l'éclairage, pas d'ombres portées
    intensity = compute_lighting(P, N, V, closest_sphere.specular, lights)
    
    r = closest_sphere.color[0] * intensity
    g = closest_sphere.color[1] * intensity
    b = closest_sphere.color[2] * intensity
    
    return (min(255, int(r)), min(255, int(g)), min(255, int(b)))

def put_pixel(x, y, color):
    sx = int(WIDTH / 2 + x)
    sy = int(HEIGHT / 2 - y) - 1 # J'ai remis la correction d'index (-1)
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        framebuffer[sx + sy * WIDTH] = color

def save_ppm(filename):
    with open(filename, 'w') as f:
        f.write(f"P3\n{WIDTH} {HEIGHT}\n255\n")
        for c in framebuffer: f.write(f"{c[0]} {c[1]} {c[2]}\n")
    print(f"Image générée : {filename}")

# --- 5. MAIN ---

def main():
    print("Rendu Chapitre 3 (Même scène que Chap 4, sans ombres)...")
    O = Vec3(0, 0, 0)
    
    # --- SCÈNE ALIGNÉE SUR LE CHAPITRE 4 ---
    # On garde les mêmes positions pour montrer "l'évolution" technique
    
    # 1. LA TERRE (A gauche)
    # Même position que Chap 4 : (-1.5, 0, 5)
    terre = Sphere(Vec3(-1.5, 0, 5), 1, (0, 0, 255), 500)
    
    # 2. LA LUNE (Toute petite devant)
    # Même position que Chap 4 : (-0.5, -0.6, 3)
    lune = Sphere(Vec3(-0.5, -0.6, 3), 0.4, (220, 220, 220), 20)
    
    spheres = [terre, lune]

    # LUMIÈRES (Copie exacte du Chap 4 pour avoir le même bleu)
    lights = [
        Light('ambient', 0.2), 
        Light('point', 0.6, Vec3(-5, 10, 5)), # Lumière principale (Haut-Gauche)
        Light('point', 0.3, Vec3(5, 5, 0))    # Lumière secondaire
    ]

    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            D = canvas_to_viewport(x, y)
            color = trace_ray(O, D, 1, float('inf'), spheres, lights)
            put_pixel(x, y, color)

    save_ppm("chapitre3_evolution.ppm")

if __name__ == "__main__":
    main()