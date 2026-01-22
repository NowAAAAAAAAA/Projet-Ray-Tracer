import math
import sys

WIDTH = 400
HEIGHT = 400
MAX_RECURSION_DEPTH = 3
framebuffer = [(0, 0, 0)] * (WIDTH * HEIGHT)

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

class Sphere:
    def __init__(self, center, radius, color, specular, reflective, emissive):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular      
        self.reflective = reflective  
        self.emissive = emissive      

class Light:
    def __init__(self, l_type, intensity, position=None):
        self.type = l_type
        self.intensity = intensity
        self.position = position

def load_scene(filename):
    spheres = []
    lights = []    
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                parts = line.split()
                obj_type = parts[0]
                
                if obj_type == 'SPHERE':
                    pos = Vec3(float(parts[1]), float(parts[2]), float(parts[3]))
                    radius = float(parts[4])
                    col = (int(parts[5]), int(parts[6]), int(parts[7]))
                    spec = int(parts[8])
                    refl = float(parts[9])
                    emissive = 0
                    if len(parts) > 10:
                        emissive = int(parts[10])
                    spheres.append(Sphere(pos, radius, col, spec, refl, emissive))
                    
                elif obj_type == 'LIGHT':
                    l_type = parts[1]
                    ints = float(parts[2])
                    pos = None
                    if l_type == 'point':
                        pos = Vec3(float(parts[3]), float(parts[4]), float(parts[5]))
                    lights.append(Light(l_type, ints, pos))
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    return spheres, lights

def intersect_ray_sphere(ray_origin, ray_direction, sphere):
    center_to_origin = ray_origin - sphere.center

    a = ray_direction.dot(ray_direction)
    b = 2 * center_to_origin.dot(ray_direction)
    c = center_to_origin.dot(center_to_origin) - sphere.radius**2

    delta = b*b - 4*a*c
    if delta < 0: return float('inf'), float('inf')
    
    t1 = (-b + math.sqrt(delta)) / (2*a)
    t2 = (-b - math.sqrt(delta)) / (2*a)
    return t1, t2

def closest_intersection(ray_origin, ray_direction, min_t, max_t, spheres):
    closest_t = float('inf')
    closest_sphere = None
    
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(ray_origin, ray_direction, sphere)
        if min_t < t1 < max_t and t1 < closest_t:
            closest_t, closest_sphere = t1, sphere
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t, closest_sphere = t2, sphere
            
    return closest_sphere, closest_t

def compute_lighting(hit_point, surface_normal, view_vector, specular, spheres, lights):
    intensity = 0.0
    for light in lights:
        if light.type == 'ambient':
            intensity += light.intensity
        else:
            if light.type == 'point':
                light_vector = light.position - hit_point
                t_max = 1
            
            shadow_sphere, _ = closest_intersection(hit_point, light_vector, 0.001, t_max, spheres)
            if shadow_sphere is not None:
                continue 
            
            light_direction = light_vector.normalize()
            n_dot_l = surface_normal.dot(light_direction)
            
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (surface_normal.length() * light_direction.length())
            
            if specular != -1:
                reflection_vector = surface_normal * 2 * surface_normal.dot(light_direction) - light_direction
                r_dot_v = reflection_vector.dot(view_vector)
                
                if r_dot_v > 0:
                    intensity += light.intensity * pow(r_dot_v / (reflection_vector.length() * view_vector.length()), specular)
    return intensity

def reflect_ray(incident_ray, surface_normal):
    return incident_ray - surface_normal * 2 * surface_normal.dot(incident_ray)

def trace_ray(ray_origin, ray_direction, min_t, max_t, spheres, lights, recursion_depth):
    closest_sphere, closest_t = closest_intersection(ray_origin, ray_direction, min_t, max_t, spheres)

    if closest_sphere == None:
        return (0, 0, 0) 

    if closest_sphere.emissive == 1:
        return closest_sphere.color

    hit_point = ray_origin + ray_direction * closest_t
    surface_normal = (hit_point - closest_sphere.center).normalize()
    view_vector = ray_direction * -1 

    local_intensity = compute_lighting(hit_point, surface_normal, view_vector, closest_sphere.specular, spheres, lights)
    
    r = closest_sphere.color[0] * local_intensity
    g = closest_sphere.color[1] * local_intensity
    b = closest_sphere.color[2] * local_intensity

    if recursion_depth > 0 and closest_sphere.reflective > 0:
        reflected_ray_dir = reflect_ray(ray_direction, surface_normal)
        reflected_color = trace_ray(hit_point, reflected_ray_dir, 0.001, float('inf'), spheres, lights, recursion_depth - 1)
        
        k = closest_sphere.reflective
        r = r * (1 - k) + reflected_color[0] * k
        g = g * (1 - k) + reflected_color[1] * k
        b = b * (1 - k) + reflected_color[2] * k

    return (min(255, int(r)), min(255, int(g)), min(255, int(b)))

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
    print(f"Image saved: {filename}")

def main():
    print("Starting Raytracer")
    spheres, lights = load_scene("scene.txt")
    
    camera_position = Vec3(0, 0, 0)
    vw, vh, viewport_dist = 1, 1, 1
    
    print("Rendering...")
    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            ray_direction = Vec3(x * vw / WIDTH, y * vh / HEIGHT, viewport_dist)
            color = trace_ray(camera_position, ray_direction, 1, float('inf'), spheres, lights, MAX_RECURSION_DEPTH)
            put_pixel(x, y, color)

    save_ppm("final_result.ppm")

if __name__ == "__main__":
    main()