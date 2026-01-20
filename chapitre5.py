import math
import sys

# ==========================================
# CHAPITRE 5 : FINAL (SCÈNE CHARGÉE + SOLEIL ÉMISSIF)
# ==========================================

WIDTH = 400
HEIGHT = 400
MAX_RECURSION_DEPTH = 3 
framebuffer = [(0, 0, 0)] * (WIDTH * HEIGHT)

# --- 1. VECTEURS ---
class Vec3:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    def __add__(self, v): return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)
    def __sub__(self, v): return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)
    def __mul__(self, s): return Vec3(self.x * s, self.y * s, self.z * s)
    def dot(self, v): return self.x * v.x + self.y * v.y + self.z * v.z
    def length(self): return math.sqrt(self.dot(self))
    def normalize(self):
        l = self.length()
        if l == 0: return Vec3(0,0,0)
        return Vec3(self.x/l, self.y/l, self.z/l)

# --- 2. CLASSES OBJETS ---
class Sphere:
    def __init__(self, center, radius, color, specular, reflective, emissive):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular      # Brillance (-1 = mat)
        self.reflective = reflective  # Miroir (0.0 à 1.0)
        self.emissive = emissive      # Lumière (True/False ou 1/0)

class Light:
    def __init__(self, l_type, intensity, position=None):
        self.type = l_type
        self.intensity = intensity
        self.position = position

# --- 3. CHARGEMENT DE LA SCÈNE ---
def load_scene(filename):
    spheres = []
    lights = []
    print(f"--- Chargement de {filename} ---")
    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                parts = line.split()
                obj_type = parts[0]
                
                if obj_type == 'SPHERE':
                    # SPHERE x y z radius r g b specular reflective [emissive]
                    pos = Vec3(float(parts[1]), float(parts[2]), float(parts[3]))
                    radius = float(parts[4])
                    col = (int(parts[5]), int(parts[6]), int(parts[7]))
                    spec = int(parts[8])
                    refl = float(parts[9])
                    
                    # Gestion optionnelle de l'émissif (pour compatibilité)
                    emissive = 0
                    if len(parts) > 10:
                        emissive = int(parts[10])

                    spheres.append(Sphere(pos, radius, col, spec, refl, emissive))
                    
                elif obj_type == 'LIGHT':
                    # LIGHT type intensity [x y z]
                    l_type = parts[1]
                    ints = float(parts[2])
                    pos = None
                    if l_type == 'point':
                        pos = Vec3(float(parts[3]), float(parts[4]), float(parts[5]))
                    lights.append(Light(l_type, ints, pos))
                    
    except FileNotFoundError:
        print(f"ERREUR CRITIQUE : Le fichier '{filename}' n'existe pas !")
        sys.exit(1)

    return spheres, lights

# --- 4. MATHS D'INTERSECTION ---
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

def closest_intersection(O, D, min_t, max_t, spheres):
    closest_t = float('inf')
    closest_sphere = None
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(O, D, sphere)
        if min_t < t1 < max_t and t1 < closest_t:
            closest_t, closest_sphere = t1, sphere
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t, closest_sphere = t2, sphere
    return closest_sphere, closest_t

# --- 5. MOTEUR PHYSIQUE (LUMIÈRE & REFLETS) ---
def compute_lighting(P, N, V, specular, spheres, lights):
    intensity = 0.0
    for light in lights:
        if light.type == 'ambient':
            intensity += light.intensity
        else:
            if light.type == 'point':
                L_vector = light.position - P
                t_max = 1
                L = L_vector
            
            # --- OMBRES ---
            shadow_sphere, shadow_t = closest_intersection(P, L, 0.001, t_max, spheres)
            if shadow_sphere is not None:
                continue 
            
            # --- DIFFUSE ---
            L_dir = L.normalize()
            n_dot_l = N.dot(L_dir)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (N.length() * L_dir.length())
            
            # --- SPÉCULAIRE ---
            if specular != -1:
                R = N * 2 * N.dot(L_dir) - L_dir
                r_dot_v = R.dot(V)
                if r_dot_v > 0:
                    intensity += light.intensity * pow(r_dot_v / (R.length() * V.length()), specular)
    return intensity

def reflect_ray(R, N):
    return R - N * 2 * N.dot(R)

def trace_ray(O, D, min_t, max_t, spheres, lights, recursion_depth):
    closest_sphere, closest_t = closest_intersection(O, D, min_t, max_t, spheres)

    if closest_sphere == None:
        return (0, 0, 0) # Fond noir

    # --- FIX SOLEIL : Si l'objet émet de la lumière, on renvoie sa couleur brute ---
    if closest_sphere.emissive == 1:
        return closest_sphere.color

    # --- CALCULS NORMAUX ---
    P = O + D * closest_t
    N = (P - closest_sphere.center).normalize()
    V = D * -1 

    local_intensity = compute_lighting(P, N, V, closest_sphere.specular, spheres, lights)
    
    r = closest_sphere.color[0] * local_intensity
    g = closest_sphere.color[1] * local_intensity
    b = closest_sphere.color[2] * local_intensity

    # --- RÉFLEXION ---
    if recursion_depth > 0 and closest_sphere.reflective > 0:
        R = reflect_ray(D, N)
        reflected_color = trace_ray(P, R, 0.001, float('inf'), spheres, lights, recursion_depth - 1)
        k = closest_sphere.reflective
        r = r * (1 - k) + reflected_color[0] * k
        g = g * (1 - k) + reflected_color[1] * k
        b = b * (1 - k) + reflected_color[2] * k

    return (min(255, int(r)), min(255, int(g)), min(255, int(b)))

# --- 6. UTILITAIRES ---
def put_pixel(x, y, color):
    # Conversion + Sécurité anti-crash
    sx = int(WIDTH / 2 + x)
    sy = int(HEIGHT / 2 - y) - 1
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        index = sx + sy * WIDTH
        framebuffer[index] = color

def save_ppm(filename):
    with open(filename, 'w') as f:
        f.write(f"P3\n{WIDTH} {HEIGHT}\n255\n")
        for c in framebuffer: f.write(f"{c[0]} {c[1]} {c[2]}\n")
    print(f"✅ Image sauvegardée : {filename}")

# --- 7. MAIN ---
def main():
    print("🚀 Démarrage du Raytracer Chapitre 5")
    
    # 1. On charge le fichier texte
    spheres, lights = load_scene("scene.txt")
    
    O = Vec3(0, 0, 0)
    vw, vh, d = 1, 1, 1
    
    # 2. Boucle principale
    print("📷 Calcul des pixels en cours...")
    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            D = Vec3(x * vw / WIDTH, y * vh / HEIGHT, d)
            color = trace_ray(O, D, 1, float('inf'), spheres, lights, MAX_RECURSION_DEPTH)
            put_pixel(x, y, color)

    save_ppm("resultat_final.ppm")

if __name__ == "__main__":
    main()