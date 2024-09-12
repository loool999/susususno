import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm
import os
import random

class Object:
    def __init__(self, obj_type, x, y, rotation, scale, color):
        self.obj_type = obj_type
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scale = scale
        self.color = color

def load_objects(folder_path):
    objects = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            obj_path = os.path.join(folder_path, filename)
            obj_image = cv2.imread(obj_path, cv2.IMREAD_UNCHANGED)
            objects.append(obj_image)
    return objects

def preprocess_image(image_path):
    return cv2.imread(image_path)

def generate_initial_population(num_objects, image_shape, available_objects):
    population = []
    for _ in range(num_objects):
        obj_type = random.choice(available_objects)
        x = random.randint(0, image_shape[1])
        y = random.randint(0, image_shape[0])
        rotation = random.uniform(0, 360)
        scale = random.uniform(0.5, 2.0)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        population.append(Object(obj_type, x, y, rotation, scale, color))
    return population

def calculate_fitness(object, target_image, canvas):
    # Create a mask for the object
    obj_mask = np.zeros(canvas.shape[:2], dtype=np.uint8)
    obj_coords = np.array([(object.x, object.y)])
    cv2.drawContours(obj_mask, [obj_coords], 0, 255, -1)

    # Calculate color difference
    obj_area = cv2.bitwise_and(canvas, canvas, mask=obj_mask)
    target_area = cv2.bitwise_and(target_image, target_image, mask=obj_mask)
    diff = cv2.absdiff(obj_area, target_area)
    return -np.sum(diff)  # Negative sum because lower difference is better

def mutate_object(obj, image_shape, mutation_rate=0.1):
    if random.random() < mutation_rate:
        obj.x = max(0, min(obj.x + random.randint(-10, 10), image_shape[1]))
    if random.random() < mutation_rate:
        obj.y = max(0, min(obj.y + random.randint(-10, 10), image_shape[0]))
    if random.random() < mutation_rate:
        obj.rotation = (obj.rotation + random.uniform(-15, 15)) % 360
    if random.random() < mutation_rate:
        obj.scale = max(0.1, obj.scale + random.uniform(-0.1, 0.1))
    if random.random() < mutation_rate:
        obj.color = tuple(max(0, min(c + random.randint(-20, 20), 255)) for c in obj.color)
    return obj

def create_new_generation(population, fitness_scores, elite_size=2):
    sorted_population = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]
    new_generation = sorted_population[:elite_size]
    
    while len(new_generation) < len(population):
        parent = random.choice(sorted_population[:len(population)//2])
        child = mutate_object(Object(parent.obj_type, parent.x, parent.y, parent.rotation, parent.scale, parent.color),
                              (target_image.shape[0], target_image.shape[1]))
        new_generation.append(child)
    
    return new_generation

def draw_objects(canvas, population, available_objects):
    for obj in population:
        obj_image = obj.obj_type
        obj_image = cv2.resize(obj_image, None, fx=obj.scale, fy=obj.scale)
        obj_image = cv2.warpAffine(obj_image, cv2.getRotationMatrix2D((obj_image.shape[1]//2, obj_image.shape[0]//2), obj.rotation, 1.0), obj_image.shape[:2][::-1])
        
        x, y = int(obj.x - obj_image.shape[1]//2), int(obj.y - obj_image.shape[0]//2)
        
        # Calculate the valid region to draw
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(canvas.shape[1], x + obj_image.shape[1]), min(canvas.shape[0], y + obj_image.shape[0])
        
        # Calculate the corresponding region in the object image
        obj_x1, obj_y1 = x1 - x, y1 - y
        obj_x2, obj_y2 = obj_x1 + (x2 - x1), obj_y1 + (y2 - y1)
        
        if x2 > x1 and y2 > y1 and obj_x2 > obj_x1 and obj_y2 > obj_y1:
            if obj_image.shape[2] == 4:  # If the image has an alpha channel
                alpha = obj_image[obj_y1:obj_y2, obj_x1:obj_x2, 3] / 255.0
                alpha = np.expand_dims(alpha, axis=2)
                for c in range(3):
                    canvas[y1:y2, x1:x2, c] = \
                        (1 - alpha[:,:,0]) * canvas[y1:y2, x1:x2, c] + \
                        alpha[:,:,0] * obj_image[obj_y1:obj_y2, obj_x1:obj_x2, c] * (obj.color[c] / 255.0)
            else:
                canvas[y1:y2, x1:x2] = obj_image[obj_y1:obj_y2, obj_x1:obj_x2] * (np.array(obj.color) / 255.0)
    
    return canvas

def main():
    target_image_path = "image.jpg"
    output_image_path = "output.jpg"
    objects_folder = "object"
    num_generations = 100
    population_size = 50

    target_image = preprocess_image(target_image_path)
    canvas = preprocess_image(output_image_path)
    available_objects = load_objects(objects_folder)

    population = generate_initial_population(population_size, target_image.shape, available_objects)

    for generation in tqdm(range(num_generations), desc="Generations"):
        canvas_copy = canvas.copy()
        canvas_copy = draw_objects(canvas_copy, population, available_objects)

        fitness_scores = [calculate_fitness(obj, target_image, canvas_copy) for obj in population]
        
        population = create_new_generation(population, fitness_scores)

        if generation % 10 == 0:
            cv2.imwrite(f"generation_{generation}.jpg", canvas_copy)

    final_canvas = draw_objects(canvas.copy(), population, available_objects)
    cv2.imwrite("final_output.jpg", final_canvas)

    similarity = calculate_similarity(cv2.absdiff(final_canvas, target_image))
    print(f"Final similarity: {similarity:.2f}%")

if __name__ == "__main__":
    main()