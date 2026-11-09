#!/usr/bin/env node
// Agrega una versión de una app al source (apps.json) y copia el .ipa a ipas/.
//
// Uso:
//   node add-release.mjs <App> <ruta.ipa> <versión> ["notas de la versión"]
//   node add-release.mjs ScoreHide ../score-spoiler-local-ios/ScoreHide.ipa 1.7.0 "Versión inicial."
//
// App nueva (no está en apps.json): agrega --bundle y, opcionalmente, --subtitle, --description, --tint.
//   node add-release.mjs PlexLocal ../plexamp-/plexamp-local-ios/build/PlexLocal.ipa 0.1.0 "Primera versión." \
//        --bundle com.loera.plexlocal.ios --subtitle "Música de tu servidor Plex"

import { copyFileSync, existsSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Dirección pública donde queda esta carpeta (repo público de GitHub, rama main).
const BASE_URL = 'https://raw.githubusercontent.com/rolandoloera/ios-apps/main';
const MIN_OS = '17.0';

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, 'apps.json');

const positional = [];
const flags = {};
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) flags[argv[i].slice(2)] = argv[++i];
  else positional.push(argv[i]);
}
const [appName, ipaPath, version, notes = `Versión ${version}.`] = positional;

function fail(msg) {
  console.error(`Error: ${msg}`);
  process.exit(1);
}

if (!appName || !ipaPath || !version) {
  fail('uso: node add-release.mjs <App> <ruta.ipa> <versión> ["notas"] [--bundle id]');
}
if (!existsSync(ipaPath)) fail(`no existe ${ipaPath}`);
if (!/^\d+(\.\d+){0,3}$/.test(version)) fail(`la versión debe ser como 1.7.0 (llegó "${version}")`);

const source = JSON.parse(readFileSync(sourcePath, 'utf8'));
let app = source.apps.find(a => a.name.toLowerCase() === appName.toLowerCase());

if (!app) {
  if (!flags.bundle) fail(`"${appName}" no está en apps.json; para agregarla pasa --bundle com.loera.algo`);
  app = {
    name: appName,
    bundleIdentifier: flags.bundle,
    developerName: source.apps[0]?.developerName ?? 'Rolando Loera',
    subtitle: flags.subtitle ?? '',
    localizedDescription: flags.description ?? flags.subtitle ?? appName,
    iconURL: `${BASE_URL}/icons/${appName}.png`,
    ...(flags.tint ? { tintColor: flags.tint.replace('#', '') } : {}),
    versions: [],
    permissions: [],
  };
  source.apps.push(app);
  if (!existsSync(join(here, 'icons', `${appName}.png`))) {
    console.warn(`Aviso: falta icons/${appName}.png (copia el icon-1024.png de la app).`);
  }
}

const fileName = `${app.name}-${version}.ipa`;
copyFileSync(ipaPath, join(here, 'ipas', fileName));
const size = statSync(join(here, 'ipas', fileName)).size;

const now = new Date();
const date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

// Si la versión ya existía (se volvió a compilar), se reemplaza; la más nueva va primero.
app.versions = app.versions.filter(v => v.version !== version);
app.versions.unshift({
  version,
  date,
  localizedDescription: notes,
  downloadURL: `${BASE_URL}/ipas/${fileName}`,
  size,
  minOSVersion: flags['min-os'] ?? MIN_OS,
});

writeFileSync(sourcePath, JSON.stringify(source, null, 2) + '\n', 'utf8');
console.log(`${app.name} ${version} → ipas/${fileName} (${(size / 1024 / 1024).toFixed(2)} MB)`);
console.log(`Source: ${BASE_URL}/apps.json`);
