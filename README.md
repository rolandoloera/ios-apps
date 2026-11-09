# ios-releases

Source de AltStore / SideStore / Feather con mis apps (`apps.json`) y sus `.ipa`.

URL del source: `https://raw.githubusercontent.com/rolandoloera/ios-apps/main/apps.json`

## Publicar una versión nueva

```bash
node add-release.mjs ScoreHide ../score-spoiler-local-ios/ScoreHide.ipa 1.8.0 "Qué cambió"
git add -A && git commit -m "ScoreHide 1.8.0" && git push
```

El script copia el `.ipa` a `ipas/<App>-<versión>.ipa` y agrega la versión al inicio de `versions` con la fecha, el tamaño y el `downloadURL`. Si vuelves a publicar la misma versión, reemplaza la entrada anterior.

## Agregar otra app

1. Copia su `icon-1024.png` a `icons/<App>.png`.
2. Agrega `--bundle` la primera vez:

```bash
node add-release.mjs PlexLocal ../plexamp-/plexamp-local-ios/build/PlexLocal.ipa 0.1.0 "Primera versión." --bundle com.loera.plexlocal.ios --subtitle "Música de tu servidor Plex"
```

Para cambiar la descripción, el subtítulo o el color de una app, edita `apps.json` a mano.
