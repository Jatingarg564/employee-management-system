import io
import uuid

from PIL import Image, UnidentifiedImageError
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError


ALLOWED_IMAGE_FORMATS = {
    "JPEG": "JPEG",
    "PNG": "PNG",
    "WEBP": "WEBP",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 4096


def sanitize_profile_photo(uploaded_file):
    """
    Validate and sanitize an employee profile photo.

    The uploaded file is decoded by Pillow and then re-encoded
    into a newly generated image. The original file bytes,
    filename, and metadata are not preserved.
    """

    if uploaded_file is None:
        return None

    if uploaded_file.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            "Profile photo must not exceed 5 MB."
        )

    try:
        image = Image.open(uploaded_file)
        image.verify()
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
    ):
        raise ValidationError(
            "The uploaded profile photo is not a valid image."
        )

    uploaded_file.seek(0)

    try:
        image = Image.open(uploaded_file)
        image.load()
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
    ):
        raise ValidationError(
            "The uploaded profile photo could not be processed."
        )

    image_format = image.format

    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError(
            "Profile photo must be a JPEG, PNG, or WebP image."
        )

    width, height = image.size

    if (
        width > MAX_IMAGE_DIMENSION
        or height > MAX_IMAGE_DIMENSION
    ):
        raise ValidationError(
            "Profile photo dimensions must not exceed "
            "4096 x 4096 pixels."
        )

    if image_format == "JPEG":
        sanitized_image = image.convert("RGB")
    elif image_format == "PNG":
        if image.mode not in ("RGB", "RGBA"):
            sanitized_image = image.convert("RGBA")
        else:
            sanitized_image = image.copy()
    else:
        if image.mode not in ("RGB", "RGBA"):
            sanitized_image = image.convert("RGBA")
        else:
            sanitized_image = image.copy()

    output = io.BytesIO()

    save_kwargs = {
        "format": ALLOWED_IMAGE_FORMATS[image_format],
    }

    if image_format == "JPEG":
        save_kwargs["quality"] = 90
        save_kwargs["optimize"] = True

    elif image_format == "PNG":
        save_kwargs["optimize"] = True

    elif image_format == "WEBP":
        save_kwargs["quality"] = 90
        save_kwargs["method"] = 6

    sanitized_image.save(
        output,
        **save_kwargs,
    )

    sanitized_image.close()

    output.seek(0)

    extension = image_format.lower()

    filename = (
        f"employee_{uuid.uuid4().hex}.{extension}"
    )

    return ContentFile(
        output.read(),
        name=filename,
    )