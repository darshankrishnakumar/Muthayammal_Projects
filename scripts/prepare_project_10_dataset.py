import os
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter
import cv2

base_dir = "/Users/eash/Documents/antigravity/excited-borg/project_10_deepfake_detector/source_code/data"
sample_dir = os.path.join(base_dir, "sample_faces")
os.makedirs(sample_dir, exist_ok=True)

np.random.seed(42)

print("=== Generating Curated Face Samples for PROJECT-010 ===")

def create_face_canvas(is_fake=False, fake_type="stylegan"):
    # Create 256x256 image with natural portrait lighting
    img = Image.new("RGB", (256, 256), color=(30, 35, 45))
    draw = ImageDraw.Draw(img)
    
    # Background gradient
    for y in range(256):
        c = int(25 + 20 * (y / 256))
        draw.line([(0, y), (256, y)], fill=(c, c + 5, c + 15))
        
    # Face Oval
    skin_tone = (225, 185, 155) if not is_fake else (235, 175, 160)
    draw.ellipse([50, 40, 206, 220], fill=skin_tone)
    
    # Hair
    draw.ellipse([45, 25, 211, 100], fill=(40, 25, 15))
    
    # Eyes
    draw.ellipse([80, 110, 105, 125], fill=(255, 255, 255))
    draw.ellipse([151, 110, 176, 125], fill=(255, 255, 255))
    # Pupils
    draw.ellipse([90, 114, 100, 124], fill=(30, 20, 10))
    draw.ellipse([161, 114, 171, 124], fill=(30, 20, 10))
    
    # Eyebrows
    draw.arc([75, 95, 110, 110], start=180, end=360, fill=(40, 25, 15), width=3)
    draw.arc([146, 95, 181, 110], start=180, end=360, fill=(40, 25, 15), width=3)
    
    # Nose
    draw.line([(128, 125), (124, 155)], fill=(180, 140, 110), width=2)
    draw.line([(124, 155), (132, 155)], fill=(180, 140, 110), width=2)
    
    # Mouth
    mouth_color = (200, 100, 95) if not is_fake else (215, 90, 105)
    draw.ellipse([105, 175, 151, 190], fill=mouth_color)
    draw.line([(108, 182), (148, 182)], fill=(150, 70, 70), width=2)
    
    # Natural Gaussian smoothing
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    arr = np.array(img, dtype=np.float32)

    # Add realistic sensor noise
    noise = np.random.normal(0, 3.5, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)

    if is_fake:
        if fake_type == "stylegan":
            # GAN periodic artifact (checkerboard high frequency noise)
            y_indices, x_indices = np.indices((256, 256))
            checker = ((x_indices // 4 + y_indices // 4) % 2) * 12.0
            arr = np.clip(arr + np.stack([checker]*3, axis=-1), 0, 255).astype(np.uint8)
        elif fake_type == "faceswap":
            # Blending seam artifact around facial contour
            mask = np.zeros((256, 256), dtype=np.uint8)
            cv2.ellipse(mask, (128, 140), (60, 75), 0, 0, 360, 255, 3)
            seam = cv2.GaussianBlur(mask, (5, 5), 0)
            arr = np.clip(arr + np.stack([seam * 0.25]*3, axis=-1), 0, 255).astype(np.uint8)
        elif fake_type == "diffusion":
            # Color chromaticity saturation mismatch & blur artifact
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.35, 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.08, 0, 255)
            arr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    return Image.fromarray(arr)

# Save preset samples
samples = [
    ("real_person_01.jpg", False, "authentic"),
    ("real_person_02.jpg", False, "authentic"),
    ("deepfake_faceswap_01.jpg", True, "faceswap"),
    ("deepfake_stylegan_01.jpg", True, "stylegan"),
    ("deepfake_diffusion_01.jpg", True, "diffusion")
]

for fname, is_fake, ftype in samples:
    img = create_face_canvas(is_fake, ftype)
    p = os.path.join(sample_dir, fname)
    img.save(p, quality=95)
    print(f"Saved sample: {p} (Fake: {is_fake}, Type: {ftype})")

# 2. Generate 1,000 dataset rows
print("\nGenerating 1,000-sample Deepfake Forensics Dataset CSV...")
records = []

for i in range(1, 1001):
    is_fake = 1 if i > 500 else 0
    if not is_fake:
        m_type = "authentic"
        fft_ratio = np.random.normal(0.18, 0.04) # Low high-frequency anomaly
        chroma_var = np.random.normal(12.5, 2.5)  # Natural color variance
        boundary_seam = np.random.normal(0.08, 0.03) # No blending seam
        eye_asym = np.random.normal(0.05, 0.02)
        laplacian_var = np.random.normal(320.0, 45.0) # High sharpness
    else:
        ft = np.random.choice(["deepfake_faceswap", "stylegan_synthesis", "diffusion_inpainting"])
        m_type = ft
        if ft == "stylegan_synthesis":
            fft_ratio = np.random.normal(0.72, 0.08) # High spectral checkerboard
            chroma_var = np.random.normal(24.0, 4.0)
            boundary_seam = np.random.normal(0.25, 0.06)
            eye_asym = np.random.normal(0.18, 0.05)
            laplacian_var = np.random.normal(240.0, 35.0)
        elif ft == "deepfake_faceswap":
            fft_ratio = np.random.normal(0.48, 0.07)
            chroma_var = np.random.normal(28.5, 5.0)
            boundary_seam = np.random.normal(0.82, 0.08) # High boundary seam discontinuity
            eye_asym = np.random.normal(0.15, 0.04)
            laplacian_var = np.random.normal(190.0, 30.0)
        else: # diffusion_inpainting
            fft_ratio = np.random.normal(0.65, 0.09)
            chroma_var = np.random.normal(32.0, 6.0) # High saturation distortion
            boundary_seam = np.random.normal(0.60, 0.07)
            eye_asym = np.random.normal(0.28, 0.06) # Eye/iris asymmetry
            laplacian_var = np.random.normal(210.0, 40.0)

    records.append({
        "sample_id": f"FACE_{i:04d}",
        "label": is_fake,
        "label_name": "DEEPFAKE" if is_fake else "REAL",
        "manipulation_type": m_type,
        "fft_high_freq_ratio": max(0.01, round(float(fft_ratio), 4)),
        "color_chroma_variance": max(1.0, round(float(chroma_var), 4)),
        "boundary_gradient_discontinuity": max(0.01, round(float(boundary_seam), 4)),
        "eye_asymmetry_index": max(0.01, round(float(eye_asym), 4)),
        "laplacian_blur_metric": max(50.0, round(float(laplacian_var), 4))
    })

df = pd.DataFrame(records)
csv_path = os.path.join(base_dir, "deepfake_dataset.csv")
df.to_csv(csv_path, index=False)
print(f"=== Saved 1,000 Dataset Records to {csv_path} ===")
