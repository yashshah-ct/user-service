from io import BytesIO
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from PIL import Image

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


def load_notification_template() -> Environment:
    return Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)


def render_welcome_email(full_name: str, email: str) -> str:
    env = load_notification_template()
    template = env.get_template("welcome.html")
    return template.render(full_name=full_name, email=email)


def normalize_avatar_png(raw: bytes, max_edge: int = 256) -> bytes:
    with Image.open(BytesIO(raw)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_edge, max_edge))
        out = BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()


def parse_sort_overrides(raw: str) -> dict[str, str]:
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}
