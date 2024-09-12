import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

def calculate_heatmap(image_path: str, points_range: int = 175) -> float:
    # Open image as grayscale
    with Image.open(image_path).convert("L") as img:
        img_array = np.array(img) / 255.0  # Normalize pixel values between 0 and 1

    # Calculate points directly from the grayscale intensities
    points = img_array * points_range
    return np.sum(points)

def color_difference(
    image_path1: str,
    image_path2: str,
    output_heatmap_path: str,
    just_heatmap_path: str,
    vmin: int = 0,
    vmax: int = 255
) -> np.ndarray:
    
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    if img1 is None or img2 is None:
        raise ValueError("Error: One of the image paths is incorrect or the images couldn't be loaded.")

    if img1.shape != img2.shape:
        print("Resizing second image to match the first image.")
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    diff = cv2.absdiff(img1, img2)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    plt.figure(figsize=(10, 8))
    plt.imshow(diff_gray, cmap="jet", vmin=vmin, vmax=vmax)
    plt.colorbar()
    plt.savefig(output_heatmap_path)
    plt.close()

    plt.imsave(just_heatmap_path, diff_gray, cmap="jet", vmin=vmin, vmax=vmax)

    return diff_gray

def calculate_similarity(diff: np.ndarray) -> float:
    max_diff = 255 * diff.size
    actual_diff = np.sum(diff)
    return (1 - (actual_diff / max_diff)) * 100

def display_progress_bar(similarity: float) -> None:
    with tqdm(total=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}%") as progress:
        progress.n = int(similarity)
        progress.update(0)

def main():

    image1_path = "image.jpg"
    image2_path = "output.jpg"
    output_heatmap_path = "heatmap.jpg"
    only_heatmap_path = "heatmap2.jpg"
    vmin, vmax = -20, 180

    diff = color_difference(image1_path, image2_path, output_heatmap_path, only_heatmap_path, vmin, vmax)

    similarity = calculate_similarity(diff)
    display_progress_bar(similarity)

    total_points = calculate_heatmap(only_heatmap_path)

    print(f"Total Points: {total_points}")
    print(f"Similarity: {similarity:.10f}%")

if __name__ == "__main__":
    main()
