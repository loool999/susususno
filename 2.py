import os
import numpy as np
import cv2
import random
from tqdm import tqdm

# Load the target image
TARGET_IMAGE_PATH = "image.jpg"
OUTPUT_FOLDER = "output_images"
NEW_OBJECTS_DIR = "object"
GENERATIONS = 100
POPULATION_SIZE = 50
SURVIVORS = 20
MUTATION_RATE = 0.1

# Preprocessing: Load the target image
target_image = cv2.imread(TARGET_IMAGE_PATH)
image_h, image_w = target_image.shape[:2]

# Create an empty canvas (same size as target image)
canvas = np.zeros_like(target_image)

# Load object images from the objects folder
object_images = [cv2.imread(os.path.join(NEW_OBJECTS_DIR, f)) for f in os.listdir(NEW_OBJECTS_DIR) if f.endswith(('png', 'jpg'))]

# Object class to represent each drawable object
class Object:
    def __init__(self):
        self.image = random.choice(object_images)
        
        # Ensure object size fits within canvas bounds
        object_h, object_w = self.image.shape[:2]
        
        if object_w > image_w or object_h > image_h:
            # Resize the object to fit within the canvas
            scale_factor_w = image_w / object_w
            scale_factor_h = image_h / object_h
            scale_factor = min(scale_factor_w, scale_factor_h)  # Ensure the object fits both width and height
            
            # Resize the image
            new_width = int(object_w * scale_factor)
            new_height = int(object_h * scale_factor)
            self.image = cv2.resize(self.image, (new_width, new_height))
        
        # Update the object size after resizing
        self.size = self.image.shape[:2]
        
        # Random position, ensuring the object doesn't exceed canvas boundaries
        self.x = random.randint(0, image_w - self.size[1])
        self.y = random.randint(0, image_h - self.size[0])
        
        # Random rotation and scale
        self.rotation = random.randint(0, 360)
        self.scale = random.uniform(0.5, 1.5)

# Fitness function: Compare canvas to target image
def fitness(canvas, target):
    return np.sum(np.abs(canvas.astype(np.int32) - target.astype(np.int32)))

# Initialize population
def initialize_population():
    return [Object() for _ in range(POPULATION_SIZE)]

# Create a new generation by selecting survivors and mutating them
def create_new_generation(objects):
    global canvas
    scores = []
    
    for obj in objects:
        # Clear the canvas before drawing the object
        canvas.fill(0)
        
        # Draw the object onto the canvas
        obj.draw(canvas)
        
        # Calculate fitness of the current canvas vs the target image
        score = fitness(canvas, target_image)
        scores.append((score, obj))
    
    # Sort the objects by fitness score (lower score is better)
    objects = [obj for _, obj in sorted(scores, key=lambda x: x[0])]
    
    # Select the top survivors
    survivors = objects[:SURVIVORS]
    
    # Generate new population with mutations
    new_generation = []
    for obj in survivors:
        new_obj = Object()
        new_obj.mutate()
        new_generation.append(new_obj)
    
    return new_generation

# Main loop
def main():
    # Create the output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    population = initialize_population()

    for generation in range(GENERATIONS):
        # Create new generation
        population = create_new_generation(population)
        
        # Clear the canvas and draw the best object
        canvas.fill(0)
        best_obj = population[0]
        best_obj.draw(canvas)
        
        # Save the best canvas for each generation
        generation_image_path = os.path.join(OUTPUT_FOLDER, f"generation_{generation}.png")
        cv2.imwrite(generation_image_path, canvas)
        print(f"Generation {generation} saved at {generation_image_path}.")

if __name__ == "__main__":
    main()
