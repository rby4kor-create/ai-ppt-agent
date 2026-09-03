import os
import re


def create_image_filename(title: str) -> str:
    """
    Convert an article title into a safe image filename.
    """

    # Convert to lowercase
    filename = title.lower()

    # Replace non-alphanumeric characters with underscores
    filename = re.sub(r'[^a-z0-9]+', '_', filename)

    # Remove leading/trailing underscores
    filename = filename.strip('_')

    # Limit filename length (optional but recommended)
    filename = filename[:80]

    # Return full path
    return os.path.join("generated_images", f"{filename}.png")