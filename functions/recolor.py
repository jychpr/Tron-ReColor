import os
import cv2
import numpy as np

# Try to import SciPy's UnivariateSpline for advanced tone curve interpolation.
try:
    from scipy.interpolate import UnivariateSpline
    spline_available = True
except ImportError:
    spline_available = False

# Global cache for tone curve lookup tables.
tone_curve_LUT_cache = {}

def process_image(input_filepath, output_folder, comparison_folder, preset_name):
    """
    Processes the image at input_filepath using a Lightroom-like preset
    and saves:
      - The processed image to output_folder with filename: [filename]_[preset].[ext]
      - A side-by-side comparison image (saved as PNG) to comparison_folder.
    """
    # Read the image in BGR order.
    image = cv2.imread(input_filepath)
    if image is None:
        raise ValueError(f"Error: Could not open image: {input_filepath}")
    
    # Import presets.
    from .presets import presets
    if preset_name not in presets:
        raise ValueError(f"Preset '{preset_name}' not found.")
    preset = presets[preset_name]
    
    # Apply the sequence of adjustments.
    image = adjust_white_balance(image, preset.get("white_balance", {}))
    image = adjust_tone(image, preset.get("tone", {}))
    image = adjust_presence(image, preset.get("presence", {}))
    image = adjust_vibrance_saturation(image, preset.get("vibrance", 0), preset.get("saturation", 0))
    image = apply_tone_curves(image, preset.get("tone_curves", {}))
    image = adjust_hsl(image, preset.get("hsl", {}))
    image = adjust_color_grading(image, preset.get("color_grading", {}))
    image = add_grain(image, preset.get("grain", {}))
    image = adjust_calibration(image, preset.get("calibration", {}))
    
    # Build output filename: [filename]_[preset].[ext]
    original_filename = os.path.basename(input_filepath)
    file_name, ext = os.path.splitext(original_filename)
    new_filename = f"{file_name}_{preset_name}{ext}"
    output_path = os.path.join(output_folder, new_filename)
    
    # Save the processed image.
    cv2.imwrite(output_path, image)
    
    # Create and save a side-by-side comparison image.
    original_image = cv2.imread(input_filepath)  # re-read original image
    comparison_image = create_comparison_image(original_image, image)
    comparison_filename = f"compare_{file_name}_{preset_name}.png"
    comparison_path = os.path.join(comparison_folder, comparison_filename)
    cv2.imwrite(comparison_path, comparison_image)

#########################
# Adjustment Functions
#########################

def adjust_white_balance(image, white_balance):
    """
    Adjust white balance using 'temperature' and 'tint'.
    A simple channel scaling is applied.
    """
    temp = white_balance.get("temperature", 6500)
    tint = white_balance.get("tint", 0)
    # Calculate adjustment factors relative to 6500K.
    r_adjust = (temp - 6500) / 5000.0
    b_adjust = (6500 - temp) / 5000.0
    g_adjust = tint / 100.0
    image = image.astype(np.float32)
    b, g, r = cv2.split(image)
    r = np.clip(r * (1 + r_adjust), 0, 255)
    g = np.clip(g * (1 + g_adjust), 0, 255)
    b = np.clip(b * (1 + b_adjust), 0, 255)
    return cv2.merge([b, g, r]).astype(np.uint8)

def map_contrast(contrast):
    """
    Maps a Lightroom contrast value (range -100 to 100) 
    to a multiplicative factor (e.g. -100 maps to 0.5, 0 maps to 1.0, 100 maps to 1.5).
    """
    return np.interp(contrast, [-100, 0, 100], [0.5, 1.0, 1.5])

def adjust_tone(image, tone):
    """
    Adjusts overall tone using exposure and contrast.
    Uses a remapped contrast value to avoid flattening the image.
    """
    exposure = tone.get("exposure", 0.0)
    contrast = tone.get("contrast", 0)
    
    factor_exposure = 2 ** exposure  # Exposure in stops.
    image = image.astype(np.float32) * factor_exposure
    
    contrast_factor = map_contrast(contrast)
    image = (image - 128) * contrast_factor + 128
    image = np.clip(image, 0, 255).astype(np.uint8)
    
    # For very low contrast, optionally enhance local contrast using CLAHE.
    if contrast < -50:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return image

def adjust_presence(image, presence):
    """
    Enhances clarity using an unsharp mask.
    """
    clarity = presence.get("clarity", 0)
    if clarity != 0:
        sigma = 3
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        factor = clarity / 100.0
        sharpened = cv2.addWeighted(image, 1 + factor, blurred, -factor, 0)
        image = np.clip(sharpened, 0, 255).astype(np.uint8)
    return image

def adjust_vibrance_saturation(image, vibrance, saturation):
    """
    Adjusts vibrance and saturation by modifying the HSV saturation channel.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= (1 + vibrance / 100.0)
    hsv[..., 1] += saturation
    hsv[..., 1] = np.clip(hsv[..., 1], 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def apply_curve(curve):
    """
    Builds a lookup table (LUT) for a given tone curve.
    If the curve has fewer than 4 points or if spline is not available,
    linear interpolation is used.
    """
    # Create an immutable key from the curve data for caching.
    curve_key = tuple(tuple(pair) for pair in curve)
    if curve_key in tone_curve_LUT_cache:
        return tone_curve_LUT_cache[curve_key]
    
    full_range = np.arange(256, dtype=np.float32)
    # Use linear interpolation if there are fewer than 4 points or if spline isn't available.
    if (len(curve) < 4) or (not spline_available):
        lut = np.interp(full_range, [pt[0] for pt in curve], [pt[1] for pt in curve])
    else:
        x = np.array([pt[0] for pt in curve], dtype=np.float32)
        y = np.array([pt[1] for pt in curve], dtype=np.float32)
        # Set spline degree to min(3, len(curve)-1)
        k = min(3, len(curve) - 1)
        spline = UnivariateSpline(x, y, s=0, k=k)
        lut = spline(full_range)
    
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    tone_curve_LUT_cache[curve_key] = lut
    return lut

def apply_tone_curves(image, tone_curves):
    """
    Applies global (RGB) and per-channel tone curves to the image.
    """
    if "rgb" in tone_curves and tone_curves["rgb"]:
        lut_rgb = apply_curve(tone_curves["rgb"])
        image = cv2.LUT(image, lut_rgb)
    
    b, g, r = cv2.split(image)
    if "red" in tone_curves and tone_curves["red"]:
        lut_r = apply_curve(tone_curves["red"])
        r = cv2.LUT(r, lut_r)
    if "green" in tone_curves and tone_curves["green"]:
        lut_g = apply_curve(tone_curves["green"])
        g = cv2.LUT(g, lut_g)
    if "blue" in tone_curves and tone_curves["blue"]:
        lut_b = apply_curve(tone_curves["blue"])
        b = cv2.LUT(b, lut_b)
    return cv2.merge([b, g, r])

def adjust_hsl(image, hsl_params):
    """
    Performs a basic adjustment for overall luminance and saturation in HLS space.
    (A more detailed per-color adjustment would require a more complex implementation.)
    """
    hue_adj = np.mean(list(hsl_params.get("hue", {}).values() or [0]))
    sat_adj = np.mean(list(hsl_params.get("saturation", {}).values() or [0]))
    lum_adj = np.mean(list(hsl_params.get("luminance", {}).values() or [0]))
    
    hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS).astype(np.float32)
    hls[..., 1] = np.clip(hls[..., 1] + lum_adj, 0, 255)
    hls[..., 2] = np.clip(hls[..., 2] + sat_adj, 0, 255)
    hls = hls.astype(np.uint8)
    return cv2.cvtColor(hls, cv2.COLOR_HLS2BGR)

def adjust_color_grading(image, color_grading):
    """
    Applies a simple global color grading by a hue shift if specified.
    (More complex local adjustments would require additional logic.)
    """
    global_grading = color_grading.get("global")
    if global_grading:
        hue_shift = global_grading.get("hue", 0)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return image

def add_grain(image, grain_params):
    """
    Adds simulated film grain to the image.
    """
    amount = grain_params.get("amount", 0)
    if amount == 0:
        return image
    noise = np.random.normal(0, amount, image.shape).astype(np.float32)
    noisy_image = image.astype(np.float32) + noise
    noisy_image = np.clip(noisy_image, 0, 255)
    return noisy_image.astype(np.uint8)

def adjust_calibration(image, calibration):
    """
    Placeholder for calibration adjustments.
    """
    return image

def create_comparison_image(image1, image2, resize_width=800):
    """
    Combines the original and processed images side by side.
    If the combined width exceeds resize_width, the image is resized.
    """
    if image1.shape[0] != image2.shape[0]:
        image2 = cv2.resize(image2, (image2.shape[1], image1.shape[0]))
    combined = cv2.hconcat([image1, image2])
    height, width = combined.shape[:2]
    if width > resize_width:
        scale_factor = resize_width / width
        new_size = (int(width * scale_factor), int(height * scale_factor))
        combined = cv2.resize(combined, new_size, interpolation=cv2.INTER_AREA)
    return combined
