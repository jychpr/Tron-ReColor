import os
import argparse
import cv2
from functions.recolor import process_image
from functions.presets import presets

def main():
    # Define directories.
    input_dir = "input_images"
    output_dir = "output_images"
    comparison_dir = "input_output_compare_images"

    # Create output folders if needed.
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(comparison_dir, exist_ok=True)
    
    # Setup command-line arguments.
    parser = argparse.ArgumentParser(
        description="Batch Image Recoloring with Lightroom-like transformations."
    )
    parser.add_argument("--preset", type=str, default="ares",
                        help="Preset to use. Available presets: " + ", ".join(presets.keys()))
    parser.add_argument("--use_gpu", action="store_true",
                        help="Use GPU acceleration if available (optional)")
    args = parser.parse_args()
    
    preset_name = args.preset
    if preset_name not in presets:
        print(f"Error: Preset '{preset_name}' not found. Available presets: {', '.join(presets.keys())}.")
        return
    
    # Check for GPU if requested.
    if args.use_gpu:
        try:
            num_cuda = cv2.cuda.getCudaEnabledDeviceCount()
            if num_cuda > 0:
                print(f"GPU acceleration requested. {num_cuda} CUDA device(s) found. GPU processing not fully implemented; using CPU.")
            else:
                print("No CUDA-enabled GPU found. Proceeding with CPU processing.")
        except Exception as e:
            print("GPU check failed; proceeding with CPU.")
    
    # Process each image.
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            print(f"Processing {filename} with preset '{preset_name}'...")
            try:
                process_image(file_path, output_dir, comparison_dir, preset_name)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    main()
