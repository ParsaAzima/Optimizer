from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image
import pillow_avif  # noqa: F401  (registers AVIF plugin with Pillow)


class Optimizer:
    """Utility class for optimizing / converting images."""

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _check_input(input_path: str | Path) -> Path:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        return input_path

    @staticmethod
    def _prepare_output(output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    @staticmethod
    def _strip_metadata(img: Image.Image) -> Image.Image:
        """Return a copy of the image with EXIF/metadata stripped."""
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        return clean

    @staticmethod
    def _build_result(
        input_path: Path,
        output_path: Path,
        fmt: str,
    ) -> dict[str, Any]:
        input_size = input_path.stat().st_size
        output_size = output_path.stat().st_size
        saved = (
            round((1 - output_size / input_size) * 100, 2)
            if input_size > 0
            else 0.0
        )
        return {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "input_size": input_size,
            "output_size": output_size,
            "saved": saved,
            "format": fmt,
        }

    # ------------------------------------------------------------------ #
    # Generic save (core logic used by all format-specific wrappers)
    # ------------------------------------------------------------------ #

    @staticmethod
    def save(
        input_path: str | Path,
        output_path: str | Path,
        format: str,
        quality: int = 80,
        optimize: bool = True,
        progressive: bool = False,
        lossless: bool = False,
        method: int = 6,
        compress_level: int = 9,
        remove_metadata: bool = False,
        resize: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        """
        Generic save function usable for any supported format.
        Format-specific keyword arguments are ignored by formats
        that don't support them (Pillow handles this automatically
        via save_kwargs filtering below).
        """
        input_path = Optimizer._check_input(input_path)
        output_path = Optimizer._prepare_output(output_path)
        fmt = format.upper()

        with Image.open(input_path) as img:
            if remove_metadata:
                img = Optimizer._strip_metadata(img)

            if resize:
                img.thumbnail(resize)

            save_kwargs: dict[str, Any] = {"format": fmt}

            if fmt == "JPEG":
                save_kwargs.update(
                    quality=quality,
                    optimize=optimize,
                    progressive=progressive,
                )
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
            elif fmt == "PNG":
                save_kwargs.update(
                    optimize=optimize,
                    compress_level=compress_level,
                )
            elif fmt == "WEBP":
                save_kwargs.update(
                    quality=quality,
                    method=method,
                    lossless=lossless,
                )
            elif fmt == "AVIF":
                save_kwargs.update(quality=quality)
            else:
                save_kwargs.update(quality=quality)

            img.save(output_path, **save_kwargs)

        return Optimizer._build_result(input_path, output_path, fmt)

    # ------------------------------------------------------------------ #
    # Format-specific wrappers
    # ------------------------------------------------------------------ #

    @staticmethod
    def to_avif(
        input_path: str | Path,
        output_path: str | Path,
        quality: int = 80,
        remove_metadata: bool = False,
        resize: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        return Optimizer.save(
            input_path,
            output_path,
            format="AVIF",
            quality=quality,
            remove_metadata=remove_metadata,
            resize=resize,
        )

    @staticmethod
    def optimize_jpg(
        input_path: str | Path,
        output_path: str | Path,
        quality: int = 80,
        optimize: bool = True,
        progressive: bool = True,
        remove_metadata: bool = False,
        resize: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        return Optimizer.save(
            input_path,
            output_path,
            format="JPEG",
            quality=quality,
            optimize=optimize,
            progressive=progressive,
            remove_metadata=remove_metadata,
            resize=resize,
        )

    @staticmethod
    def optimize_png(
        input_path: str | Path,
        output_path: str | Path,
        optimize: bool = True,
        compress_level: int = 9,
        remove_metadata: bool = False,
        resize: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        return Optimizer.save(
            input_path,
            output_path,
            format="PNG",
            optimize=optimize,
            compress_level=compress_level,
            remove_metadata=remove_metadata,
            resize=resize,
        )

    @staticmethod
    def to_webp(
        input_path: str | Path,
        output_path: str | Path,
        quality: int = 80,
        method: int = 6,
        lossless: bool = False,
        remove_metadata: bool = False,
        resize: tuple[int, int] | None = None,
    ) -> dict[str, Any]:
        return Optimizer.save(
            input_path,
            output_path,
            format="WEBP",
            quality=quality,
            method=method,
            lossless=lossless,
            remove_metadata=remove_metadata,
            resize=resize,
        )

    # ------------------------------------------------------------------ #
    # Extra utilities
    # ------------------------------------------------------------------ #

    @staticmethod
    def resize(
        input_path: str | Path,
        output_path: str | Path,
        size: tuple[int, int],
    ) -> dict[str, Any]:
        input_path = Optimizer._check_input(input_path)
        output_path = Optimizer._prepare_output(output_path)

        with Image.open(input_path) as img:
            img = img.resize(size)
            img.save(output_path, format=img.format or output_path.suffix.lstrip(".").upper())

        return Optimizer._build_result(input_path, output_path, output_path.suffix.lstrip("."))

    @staticmethod
    def thumbnail(
        input_path: str | Path,
        output_path: str | Path,
        size: tuple[int, int],
    ) -> dict[str, Any]:
        input_path = Optimizer._check_input(input_path)
        output_path = Optimizer._prepare_output(output_path)

        with Image.open(input_path) as img:
            img.thumbnail(size)
            img.save(output_path, format=img.format or output_path.suffix.lstrip(".").upper())

        return Optimizer._build_result(input_path, output_path, output_path.suffix.lstrip("."))

    @staticmethod
    def crop(
        input_path: str | Path,
        output_path: str | Path,
        box: tuple[int, int, int, int],
    ) -> dict[str, Any]:
        input_path = Optimizer._check_input(input_path)
        output_path = Optimizer._prepare_output(output_path)

        with Image.open(input_path) as img:
            cropped = img.crop(box)
            cropped.save(output_path, format=img.format or output_path.suffix.lstrip(".").upper())

        return Optimizer._build_result(input_path, output_path, output_path.suffix.lstrip("."))

    @staticmethod
    def remove_metadata(
        input_path: str | Path,
        output_path: str | Path,
    ) -> dict[str, Any]:
        input_path = Optimizer._check_input(input_path)
        output_path = Optimizer._prepare_output(output_path)

        with Image.open(input_path) as img:
            clean = Optimizer._strip_metadata(img)
            clean.save(output_path, format=img.format or output_path.suffix.lstrip(".").upper())

        return Optimizer._build_result(input_path, output_path, output_path.suffix.lstrip("."))

    # ------------------------------------------------------------------ #
    # Batch processing
    # ------------------------------------------------------------------ #

    @staticmethod
    def batch(
        input_folder: str | Path,
        output_folder: str | Path,
        format: str = "WEBP",
        quality: int = 80,
        remove_metadata: bool = False,
        resize: tuple[int, int] | None = None,
        extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".bmp", ".tiff"),
    ) -> list[dict[str, Any]]:
        """
        Process every image in `input_folder` (non-recursive) and save the
        converted/optimized result into `output_folder`, preserving filenames
        but swapping the extension to match `format`.
        """
        input_folder = Path(input_folder)
        if not input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {input_folder}")

        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        fmt = format.upper()
        ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "AVIF": ".avif"}
        out_ext = ext_map.get(fmt, f".{fmt.lower()}")

        results: list[dict[str, Any]] = []
        for file in sorted(input_folder.iterdir()):
            if file.is_file() and file.suffix.lower() in extensions:
                output_path = output_folder / f"{file.stem}{out_ext}"
                try:
                    result = Optimizer.save(
                        file,
                        output_path,
                        format=fmt,
                        quality=quality,
                        remove_metadata=remove_metadata,
                        resize=resize,
                    )
                    results.append(result)
                except Exception as exc:  # keep batch running even if one file fails
                    results.append(
                        {
                            "input_path": str(file),
                            "output_path": str(output_path),
                            "error": str(exc),
                        }
                    )

        return results
