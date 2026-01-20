import math

# ==========================================
# CHAPITRE 4 : OMBRES ET RÉFLEXIONS (SCÈNE FLOTTANTE)
# Objectif : Montrer les planètes et les reflets dans le vide (sans le décor)
# ==========================================

WIDTH = 400
HEIGHT = 400
MAX_RECURSION_DEPTH = 3 
framebuffer = [(0, 0, 0)] * (WIDTH * HEIGHT)

# --- 1. CLASSE VECTEUR ---
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

# --- 2. OBJETS ---
# Note : Pas encore de propriété "emissive" (Lumière) ici, c'est l'amélioration du Chapitre 5
class Sphere:
    def __init__(self, center, radius, color, specular, reflective):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular      # Brillance (-1 = mat, 500 = très brillant)
        self.reflective = reflective  # Réflexion (0.0 = mat, 1.0 = miroir parfait)

class Light:
    def __init__(self, l_type, intensity, position=None):
        self.type = l_type
        self.intensity = intensity
        self.position = position

# --- 3. MATHS D'INTERSECTION ---
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

# --- 4. LUMIÈRE ET RAYTRACING RÉCURSIF ---
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
            
            # OMBRES : On vérifie si quelque chose bloque la lumière
            shadow_sphere, shadow_t = closest_intersection(P, L, 0.001, t_max, spheres)
            if shadow_sphere is not None:
                continue 
            
            L_dir = L.normalize()
            n_dot_l = N.dot(L_dir)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (N.length() * L_dir.length())
            
            if specular != -1:
                R = N * 2 * N.dot(L_dir) - L_dir
                r_dot_v = R.dot(V)
                if r_dot_v > 0:
                    intensity += light.intensity * pow(r_dot_v / (R.length() * V.length()), specular)
    return intensity

def reflect_ray(R, N):
    return R - N * 2 * N.dot(R)

def trace_ray(O, D, min_t, max_t, spheres, lights, recursion_depth):
    # 1. Intersection
    closest_sphere, closest_t = closest_intersection(O, D, min_t, max_t, spheres)

    if closest_sphere == None:
        return (0, 0, 0) # Fond Noir (Espace vide)

    # 2. Calculs au point d'impact
    P = O + D * closest_t
    N = (P - closest_sphere.center).normalize()
    V = D * -1 

    local_intensity = compute_lighting(P, N, V, closest_sphere.specular, spheres, lights)
    
    r = closest_sphere.color[0] * local_intensity
    g = closest_sphere.color[1] * local_intensity
    b = closest_sphere.color[2] * local_intensity

    # 3. Réflexion (Miroir)
    if recursion_depth > 0 and closest_sphere.reflective > 0:
        R = reflect_ray(D, N)
        reflected_color = trace_ray(P, R, 0.001, float('inf'), spheres, lights, recursion_depth - 1)
        k = closest_sphere.reflective
        r = r * (1 - k) + reflected_color[0] * k
        g = g * (1 - k) + reflected_color[1] * k
        b = b * (1 - k) + reflected_color[2] * k

    return (min(255, int(r)), min(255, int(g)), min(255, int(b)))

# --- 5. MAIN ---

def put_pixel(x, y, color):
    sx = int(WIDTH / 2 + x)
    sy = int(HEIGHT / 2 - y) - 1
    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
        index = sx + sy * WIDTH
        framebuffer[index] = color

def save_ppm(filename):
    with open(filename, 'w') as f:
        f.write(f"P3\n{WIDTH} {HEIGHT}\n255\n")
        for c in framebuffer: f.write(f"{c[0]} {c[1]} {c[2]}\n")
    print(f"Image sauvegardée : {filename}")

def main():
    print("Rendu Chapitre 4 (Scène flottante)...")
    O = Vec3(0, 0, 0)
    
    # --- SCÈNE EN DUR DANS LE CODE ---
    # Mêmes positions que le final, mais sans le sol !

    # 1. JUPITER (La géante au fond)
    jupiter = Sphere(Vec3(1.5, 1.5, 10), 2.5, (200, 160, 130), 50, 0.1)

    # 2. LA TERRE (A gauche)
    terre = Sphere(Vec3(-1.5, 0, 5), 1, (0, 0, 255), 500, 0.3)

    # 3. MARS (A droite)
    mars = Sphere(Vec3(1.8, -0.2, 4), 0.8, (200, 60, 20), 10, 0.1)

    # 4. LA LUNE (Toute petite devant)
    lune = Sphere(Vec3(-0.5, -0.6, 3), 0.4, (220, 220, 220), 20, 0.0)

    # On n'ajoute PAS le sol ici. C'est ça la "progression" vers le chap 5.
    spheres = [jupiter, terre, mars, lune]

    # Lumières (Simples)
    lights = [
        Light('ambient', 0.2),
        Light('point', 0.6, Vec3(-5, 10, 5)), 
        Light('point', 0.3, Vec3(5, 5, 0))
    ]

    vw, vh, d = 1, 1, 1
    
    print("Calcul des pixels...")
    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            D = Vec3(x * vw / WIDTH, y * vh / HEIGHT, d)
            color = trace_ray(O, D, 1, float('inf'), spheres, lights, MAX_RECURSION_DEPTH)
            put_pixel(x, y, color)

    save_ppm("chapitre4_flottant.ppm")

if __name__ == "__main__":
    main()