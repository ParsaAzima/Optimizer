# Optimizer

A lightweight Python toolkit for optimizing and converting images (JPEG, PNG, WEBP, AVIF), with a `Optimizer` class for use in code and a companion CLI for use from the terminal.

## Features

- Convert images to **JPEG**, **PNG**, **WEBP**, and **AVIF**
- Optimize file size with configurable quality / compression settings
- Resize or create thumbnails while saving
- Strip EXIF/metadata from images
- Crop a region of an image
- Batch-process an entire folder of images
- Every operation returns structured info: input/output size, % saved, format
- Fully type-hinted, uses `pathlib.Path`, validates input files, auto-creates output directories

## Requirements

- Python 3.10+
- [Pillow](https://python-pillow.org/)
- [pillow-avif-plugin](https://github.com/fdintino/pillow-avif-plugin) (for AVIF support)

## Installation

```bash
pip install pillow pillow-avif-plugin
```

Then drop `optimizer.py` (and `optimizer_cli.py` if you want the CLI) into your project.

## Project Structure

```
optimizer.py       # Optimizer class — the core library
optimizer_cli.py    # Command-line interface built on top of Optimizer
```

---

## Library Usage

```python
from optimizer import Optimizer

# Convert to WEBP
result = Optimizer.to_webp("input.png", "output.webp", quality=80)
print(result)
# {
#   "input_path": "input.png",
#   "output_path": "output.webp",
#   "input_size": 182300,
#   "output_size": 41210,
#   "saved": 77.39,
#   "format": "WEBP"
# }

# Optimize a JPEG, resize it, and strip metadata
Optimizer.optimize_jpg(
    "photo.jpg",
    "photo_optimized.jpg",
    quality=85,
    remove_metadata=True,
    resize=(1200, 1200),
)

# Batch-convert a whole folder to AVIF
results = Optimizer.batch("images/", "optimized/", format="AVIF", quality=70)
```

### API Reference

| Method | Description |
|---|---|
| `Optimizer.save(input_path, output_path, format, **opts)` | Generic save — core logic used by all format-specific methods |
| `Optimizer.optimize_jpg(input_path, output_path, quality=80, optimize=True, progressive=True, remove_metadata=False, resize=None)` | Convert/optimize to JPEG |
| `Optimizer.optimize_png(input_path, output_path, optimize=True, compress_level=9, remove_metadata=False, resize=None)` | Convert/optimize to PNG |
| `Optimizer.to_webp(input_path, output_path, quality=80, method=6, lossless=False, remove_metadata=False, resize=None)` | Convert to WEBP |
| `Optimizer.to_avif(input_path, output_path, quality=80, remove_metadata=False, resize=None)` | Convert to AVIF |
| `Optimizer.resize(input_path, output_path, size)` | Resize to exact dimensions |
| `Optimizer.thumbnail(input_path, output_path, size)` | Resize preserving aspect ratio |
| `Optimizer.crop(input_path, output_path, box)` | Crop to a `(left, top, right, bottom)` box |
| `Optimizer.remove_metadata(input_path, output_path)` | Strip EXIF/metadata only |
| `Optimizer.batch(input_folder, output_folder, format="WEBP", quality=80, remove_metadata=False, resize=None)` | Process every image in a folder |

Every method returns a `dict` (or a `list[dict]` for `batch`) with:

```python
{
    "input_path": str,
    "output_path": str,
    "input_size": int,     # bytes
    "output_size": int,    # bytes
    "saved": float,        # percentage reduction
    "format": str,
}
```

If a file doesn't exist, `FileNotFoundError` is raised. Output directories are created automatically.

---

## CLI Usage

```bash
python optimizer_cli.py <command> [arguments] [options]
```

### Commands

| Command | Description |
|---|---|
| `jpg` | Optimize / convert to JPEG |
| `png` | Optimize / convert to PNG |
| `webp` | Convert to WEBP |
| `avif` | Convert to AVIF |
| `resize` | Resize to exact dimensions |
| `thumbnail` | Resize preserving aspect ratio |
| `crop` | Crop a region of the image |
| `strip-metadata` | Remove metadata |
| `batch` | Process every image in a folder |

Run `python optimizer_cli.py <command> --help` for the full list of options for any command.

### Examples

```bash
# Convert & optimize
python optimizer_cli.py jpg input.png output.jpg --quality 85
python optimizer_cli.py webp input.png output.webp --lossless
python optimizer_cli.py png input.png output.png --remove-metadata
python optimizer_cli.py avif input.jpg output.avif --resize 800x600

# Resize / crop / thumbnail
python optimizer_cli.py resize input.jpg output.jpg --size 400x300
python optimizer_cli.py thumbnail input.jpg output.jpg --size 200x200
python optimizer_cli.py crop input.jpg output.jpg --box 0,0,300,300

# Metadata
python optimizer_cli.py strip-metadata input.jpg output.jpg

# Batch process a folder
python optimizer_cli.py batch ./images ./optimized --format webp --quality 75
```

### Sample Output

```
✓ batch_in/img0.png -> batch_out/img0.webp
  912.0B -> 270.0B (70.39% saved) [WEBP]
✓ batch_in/img1.png -> batch_out/img1.webp
  913.0B -> 270.0B (70.43% saved) [WEBP]

Total: 2 files | Succeeded: 2 | Failed: 0
Total size: 1.8KB -> 540.0B (70.41% saved)
```

Common options across most commands:

| Option | Description |
|---|---|
| `--quality INT` | Quality (0–100), default `80` |
| `--resize WIDTHxHEIGHT` | Resize while saving (e.g. `800x600`) |
| `--remove-metadata` | Strip EXIF/metadata |
| `--no-optimize` | Disable Pillow's `optimize` flag (jpg/png) |
| `--no-progressive` | Disable progressive JPEG encoding |
| `--lossless` | Lossless WEBP |
| `--method INT` | WEBP compression method (0–6) |
| `--compress-level INT` | PNG compression level (0–9) |
| `--format {JPEG,PNG,WEBP,AVIF}` | Target format for `batch` |

Exit codes: `0` on success, `1` on error (missing file, invalid arguments, etc.) — useful for scripting.

## License

MIT
