from PIL import Image
import numpy as np

def calculate_heatmap(image_path, points_range=175):

    # Load the image and convert it to RGB
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    
    # Extract red and blue channels (normalized)
    red_channel = img_array[:, :, 0]
    blue_channel = img_array[:, :, 2]
    
    # Normalize the range between red (0 points) and blue (points_range)
    # Blue contributes more to the points, and red contributes 0
    points = blue_channel * points_range  # Blue contributes fully to the points
    
    # Sum all points in the image
    total_points = np.sum(points)
    
    return total_points

heatmap_path = 'heatmap2.jpg'
total_points = calculate_heatmap(heatmap_path)
print(f"Total points for the heatmap: {total_points}")
