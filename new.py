# file path: color_difference_with_colormap.py

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def calculate_color_difference(image1_path, image2_path, output_path='color_diff_map.png'):
    # Open images
    img1 = Image.open(image1_path).convert('RGB')
    img2 = Image.open(image2_path).convert('RGB')

    # Ensure both images have the same size
    if img1.size != img2.size:
        raise ValueError("Images must have the same dimensions")

    # Convert images to numpy arrays (shape: height, width, channels)
    img1_data = np.array(img1)
    img2_data = np.array(img2)

    # Calculate the difference between images
    diff = img1_data.astype(np.float32) - img2_data.astype(np.float32)
    diff_magnitude = np.sqrt(np.sum(diff**2, axis=-1))  # Euclidean distance per pixel (RGB space)

    # Normalize the differences to a 0-1 range for visualization
    max_diff = np.max(diff_magnitude)
    if max_diff > 0:
        normalized_diff = diff_magnitude / max_diff
    else:
        normalized_diff = diff_magnitude  # If there's no difference, keep as-is

    # Use matplotlib to apply a colormap (e.g., 'jet') to the normalized difference
    colormap = cm.get_cmap('Greens')  # You can change this to any other colormap, like 'hot', 'plasma', etc.
    color_mapped_diff = colormap(normalized_diff)

    # Convert the colormap result (which is RGBA) to RGB
    color_mapped_diff = (color_mapped_diff[:, :, :3] * 255).astype(np.uint8)

    # Convert the result back to an image
    diff_image = Image.fromarray(color_mapped_diff)

    # Save the color difference map as an image
    diff_image.save(output_path)

    # Calculate the average color difference for statistical reporting
    avg_diff = np.mean(diff_magnitude)

    return avg_diff, output_path

# Example usage
if __name__ == "__main__":
    image1_path = 'image.jpg'
    image2_path = 'filled.jpg'
    avg_difference, diff_map_path = calculate_color_difference(image1_path, image2_path)
    print(f"Average color difference between images: {avg_difference}")
    print(f"Color difference map saved at: {diff_map_path}")
