#!/usr/bin/env python3
"""Genera apps.json (source de AltStore / SideStore / Feather) leyendo los .ipa de ipas/.

De cada .ipa saca del Info.plist: nombre, bundle id, versión y iOS mínimo. Lo que no viene en el
.ipa (subtítulo, descripción, color) sale de meta.json. Cada .ipa es una versión; se puede dejar
uno solo por app (se reemplaza) o varios (ScoreHide-1.7.0.ipa, ScoreHide-1.8.0.ipa...).

Notas de una versión (opcional): un .txt con el mismo nombre que el .ipa (ipas/ScoreHide-1.8.0.txt).
"""
import datetime
import json
import os
import plistlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
IPAS = ROOT / "ipas"
INFO_RE = re.compile(r"^Payload/[^/]+\.app/Info\.plist$")


def base_url(meta):
    repo = os.environ.get("GITHUB_REPOSITORY")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    if repo:
        return f"https://raw.githubusercontent.com/{repo}/{branch}"
    return meta["baseURL"].rstrip("/")


def read_info(ipa):
    with zipfile.ZipFile(ipa) as z:
        name = next((n for n in z.namelist() if INFO_RE.match(n)), None)
        if not name:
            raise ValueError("no tiene Payload/*.app/Info.plist")
        return plistlib.loads(z.read(name))


def commit_date(path):
    """Fecha del último commit que tocó el archivo; si no está en git, hoy."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    return datetime.date.today().isoformat()


def version_key(v):
    return tuple(int(p) if p.isdigit() else 0 for p in re.split(r"[.\-]", v["version"])) + (v.get("buildVersion", ""),)


def main():
    meta = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
    url = base_url(meta)
    app_meta = meta.get("apps", {})
    apps = {}

    for ipa in sorted(IPAS.glob("*.ipa")):
        try:
            info = read_info(ipa)
        except (zipfile.BadZipFile, ValueError, plistlib.InvalidFileException) as e:
            print(f"Se omite {ipa.name}: {e}", file=sys.stderr)
            continue

        bundle = info["CFBundleIdentifier"]
        name = info.get("CFBundleDisplayName") or info.get("CFBundleName") or ipa.stem
        version = info.get("CFBundleShortVersionString", "1.0")
        m = app_meta.get(bundle, {})

        notes_file = ipa.with_suffix(".txt")
        notes = notes_file.read_text(encoding="utf-8").strip() if notes_file.exists() else f"Versión {version}."

        app = apps.setdefault(bundle, {
            "name": m.get("name", name),
            "bundleIdentifier": bundle,
            "developerName": m.get("developerName", meta.get("developerName", "")),
            "subtitle": m.get("subtitle", ""),
            "localizedDescription": m.get("localizedDescription", m.get("subtitle") or name),
            "iconURL": f"{url}/icons/{quote(m.get('icon', name + '.png'))}",
            **({"tintColor": m["tintColor"]} if "tintColor" in m else {}),
            **({"category": m["category"]} if "category" in m else {}),
            "versions": [],
            "permissions": [],
        })
        icon = ROOT / "icons" / m.get("icon", name + ".png")
        if not icon.exists():
            print(f"Aviso: falta {icon.relative_to(ROOT)} para {name}", file=sys.stderr)

        entry = {
            "version": version,
            "buildVersion": str(info.get("CFBundleVersion", "")),
            "date": commit_date(ipa),
            "localizedDescription": notes,
            "downloadURL": f"{url}/ipas/{quote(ipa.name)}",
            "size": ipa.stat().st_size,
            "minOSVersion": info.get("MinimumOSVersion", "14.0"),
        }
        # Dos .ipa con la misma versión: se queda el del commit más reciente.
        app["versions"] = [v for v in app["versions"]
                           if not (v["version"] == version and v["buildVersion"] == entry["buildVersion"] and v["date"] >= entry["date"])]
        if not any(v["version"] == version and v["buildVersion"] == entry["buildVersion"] for v in app["versions"]):
            app["versions"].append(entry)
        print(f"{name} {version} ({bundle}) <- {ipa.name}")

    for app in apps.values():
        app["versions"].sort(key=version_key, reverse=True)

    source = {
        **meta["source"],
        "iconURL": f"{url}/icons/{quote(meta['source'].get('icon', 'source.png'))}",
        "apps": sorted(apps.values(), key=lambda a: a["name"].lower()),
        "news": [],
    }
    source.pop("icon", None)
    (ROOT / "apps.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"apps.json: {len(apps)} app(s). Source: {url}/apps.json")


if __name__ == "__main__":
    main()
