# ios-apps

Source de AltStore / SideStore / Feather con mis apps.

URL del source: `https://raw.githubusercontent.com/rolandoloera/ios-apps/main/apps.json`

## Publicar una versión

Sube el `.ipa` a `ipas/` y haz push. La GitHub Action [update-source.yml](.github/workflows/update-source.yml) lee el `Info.plist` de cada `.ipa` (nombre, bundle id, versión, iOS mínimo), regenera `apps.json` y lo guarda en el repo en menos de un minuto.

```bash
cp ~/score-spoiler-local-ios/build/ScoreHide.ipa ipas/
git add ipas && git commit -m "ScoreHide 1.8.0" && git push
```

- Si cada vez usas el mismo nombre (`ScoreHide.ipa`), el source solo muestra la última versión.
- Si guardas varios archivos (`ScoreHide-1.7.0.ipa`, `ScoreHide-1.8.0.ipa`), aparecen todas las versiones y la más nueva queda primero.
- Notas de la versión (opcional): un `.txt` con el mismo nombre que el `.ipa` (`ipas/ScoreHide-1.8.0.txt`). Sin él dice "Versión 1.8.0.".
- Para ver el resultado: pestaña **Actions** del repo, o abre la URL del source.

## Archivos

| Archivo | Para qué |
|---|---|
| `ipas/` | Los `.ipa`. Lo único que tienes que tocar normalmente. |
| `icons/<Nombre>.png` | Ícono de cada app (el `icon-1024.png` de su proyecto). |
| `meta.json` | Lo que no viene en el `.ipa`: subtítulo, descripción, color, categoría, por bundle id. Una app nueva funciona sin agregarla aquí. |
| `apps.json` | Lo genera la Action; no se edita a mano. |
| `scripts/build_source.py` | El generador. Para probarlo local: `python3 scripts/build_source.py`. |

## Si `git push` falla con `HTTP 400` / `RPC failed`

```bash
git config http.postBuffer 524288000
git push
```
