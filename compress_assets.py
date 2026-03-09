import os
import subprocess
import sys

try:
    from PIL import Image
except ImportError:
    print("Error: The 'Pillow' library is required. Install it with: pip install Pillow")
    sys.exit(1)

# --- CONFIGURATION ---
MAX_RESOLUTION = 2048  # Max width/height in pixels
IMAGE_QUALITY = 80      # JPG/WebP quality (1-100)
PDF_QUALITY = "/ebook"  # /screen (72dpi), /ebook (150dpi), /printer (300dpi)

# Video/Audio settings (FFMPEG required)
VIDEO_CRF = "28"        # 0–51 (23 is default, 28 is good compression, higher = lower quality)
VIDEO_PRESET = "medium" # ultrafast, fast, medium, slow, veryslow
AUDIO_BITRATE = "128k"  # Standard quality

EXTENSIONS_IMG = {'.jpg', '.jpeg', '.png', '.webp'}
EXTENSIONS_VIDEO = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
EXTENSIONS_AUDIO = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
# ---------------------

def safe_path(path):
    """Returns a string representation of the path safe for printing."""
    if isinstance(path, bytes):
        return path.decode(sys.getfilesystemencoding(), errors='replace')
    return path.encode('utf-8', 'replace').decode('utf-8')

def compress_image(file_path):
    try:
        ext = os.path.splitext(file_path.lower())[1]
        with Image.open(file_path) as img:
            orig_size = os.path.getsize(file_path)
            
            # Preserve transparency for PNG and WebP
            if ext in {'.jpg', '.jpeg'}:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
            
            # Proportional resize if too large
            if max(img.size) > MAX_RESOLUTION:
                img.thumbnail((MAX_RESOLUTION, MAX_RESOLUTION), Image.Resampling.LANCZOS)
            
            # Save (overwrites original)
            if ext == '.png':
                # PNG uses compression_level (0-9) instead of quality
                img.save(file_path, optimize=True)
            else:
                img.save(file_path, optimize=True, quality=IMAGE_QUALITY)
            
            new_size = os.path.getsize(file_path)
            return orig_size - new_size
    except Exception as e:
        print(f"Error on image {safe_path(file_path)}: {e}")
        return 0

def compress_pdf(file_path):
    temp_pdf = file_path + ".tmp"
    try:
        orig_size = os.path.getsize(file_path)
        # Ghostscript command to compress PDF
        # Use os.fsencode to handle special characters in paths
        cmd = [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={PDF_QUALITY}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            os.fsencode(f"-sOutputFile={temp_pdf}"), os.fsencode(file_path)
        ]
        subprocess.run(cmd, check=True)
        
        if os.path.exists(temp_pdf):
            new_size = os.path.getsize(temp_pdf)
            if new_size < orig_size:
                os.replace(temp_pdf, file_path)
                return orig_size - new_size
            else:
                os.remove(temp_pdf) # Keep original if compressed is larger
    except Exception as e:
        if "gs" in str(e):
            print(f"Error: Ghostscript (gs) not found or failed. PDF compression skipped for {safe_path(file_path)}")
        else:
            print(f"Error on PDF {safe_path(file_path)}: {e}")
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)
    return 0

def compress_video(file_path):
    ext = os.path.splitext(file_path)[1]
    temp_video = file_path + ".tmp" + ext
    try:
        orig_size = os.path.getsize(file_path)
        # ffmpeg: libx264 for video, aac for audio
        cmd = [
            "ffmpeg", "-i", os.fsencode(file_path),
            "-vcodec", "libx264", "-crf", VIDEO_CRF, "-preset", VIDEO_PRESET,
            "-acodec", "aac", "-b:a", AUDIO_BITRATE,
            "-y", "-loglevel", "quiet",
            os.fsencode(temp_video)
        ]
        subprocess.run(cmd, check=True)

        if os.path.exists(temp_video):
            new_size = os.path.getsize(temp_video)
            if new_size < orig_size:
                os.replace(temp_video, file_path)
                return orig_size - new_size
            else:
                os.remove(temp_video)
    except Exception as e:
        print(f"Error on video {safe_path(file_path)}. Make sure ffmpeg is installed. Error: {e}")
        if os.path.exists(temp_video):
            os.remove(temp_video)
    return 0

def compress_audio(file_path):
    ext = os.path.splitext(file_path)[1]
    temp_audio = file_path + ".tmp" + ext
    try:
        orig_size = os.path.getsize(file_path)
        # ffmpeg: re-encode to lower bitrate
        cmd = [
            "ffmpeg", "-i", os.fsencode(file_path),
            "-b:a", AUDIO_BITRATE,
            "-y", "-loglevel", "quiet",
            os.fsencode(temp_audio)
        ]
        subprocess.run(cmd, check=True)

        if os.path.exists(temp_audio):
            new_size = os.path.getsize(temp_audio)
            if new_size < orig_size:
                os.replace(temp_audio, file_path)
                return orig_size - new_size
            else:
                os.remove(temp_audio)
    except Exception as e:
        print(f"Error on audio {safe_path(file_path)}. Make sure ffmpeg is installed. Error: {e}")
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
    return 0

def main():
    total_saved = 0
    counts = {"IMG": 0, "PDF": 0, "VIDEO": 0, "AUDIO": 0}
    
    # Determine the directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Starting compression in: {safe_path(base_dir)}")
    
    for root, dirs, files in os.walk(base_dir):
        # Don't compress the script itself
        if "compress_assets.py" in files:
            files.remove("compress_assets.py")
            
        for file in files:
            try:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file.lower())[1]
                
                saved = 0
                label = ""

                if ext in EXTENSIONS_IMG:
                    saved = compress_image(file_path)
                    label = "IMG"
                elif ext == ".pdf":
                    saved = compress_pdf(file_path)
                    label = "PDF"
                elif ext in EXTENSIONS_VIDEO:
                    saved = compress_video(file_path)
                    label = "VIDEO"
                elif ext in EXTENSIONS_AUDIO:
                    saved = compress_audio(file_path)
                    label = "AUDIO"

                if saved > 0:
                    total_saved += saved
                    counts[label] += 1
                    print(f"[{label}] {safe_path(file_path)} compressed (-{saved/1024:.1f} KB)")
            except Exception as e:
                print(f"Unexpected error processing {safe_path(file)}: {e}")
                continue

    print(f"\n--- Summary ---")
    for key, val in counts.items():
        if val > 0 or key in ["IMG", "PDF"]: # Keep original labels for clarity
            print(f"{key}s processed: {val}")
    print(f"Total space saved: {total_saved / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
