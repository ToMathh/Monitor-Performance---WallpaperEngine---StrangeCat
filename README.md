```
╔══════════════════════════════════════════════════════════════════╗
║           🐱  STRANGECAT MONITOR  v3.2  —  README               ║
║           System monitor + HTTP server for Wallpaper Engine      ║
╚══════════════════════════════════════════════════════════════════╝
```

# StrangeCat Monitor

**StrangeCat Monitor** est une application de monitoring système légère pour Windows, conçue pour alimenter les **wallpapers web Wallpaper Engine** en données de performance en temps réel. Elle expose un serveur HTTP local sur `http://127.0.0.1:5100/performance` que vos wallpapers peuvent interroger via JavaScript — aucune configuration réseau requise.

Elle fonctionne aussi comme un **widget de bureau flottant**, toujours visible, redimensionnable, avec des graphiques sparkline et un mode compact.

---

## Sommaire

- [Comment ça fonctionne](#comment-ça-fonctionne)
- [Fonctionnalités](#fonctionnalités)
- [Installation rapide](#installation-rapide)
- [Créer un EXE standalone](#créer-un-exe-standalone)
- [Interface](#interface)
- [Sources de température CPU](#sources-de-température-cpu)
- [API HTTP — Wallpaper Engine](#api-http--wallpaper-engine)
- [Intégrer les données dans un wallpaper](#intégrer-les-données-dans-un-wallpaper)
- [Wallpapers compatibles](#wallpapers-compatibles)
- [Configuration](#configuration)
- [Résolution de problèmes](#résolution-de-problèmes)
- [Sécurité & vie privée](#sécurité--vie-privée)
- [Dépendances](#dépendances)
- [Historique des versions](#historique-des-versions)

---

## Comment ça fonctionne

StrangeCat Monitor fonctionne en deux parties qui travaillent ensemble :

### 1 — Le widget de bureau

Au lancement, une petite fenêtre flottante apparaît sur votre bureau. Elle interroge Windows toutes les 2 secondes pour récupérer les données de votre matériel (CPU, RAM, GPU, réseau) et les affiche sous forme de graphiques ou de barres selon le mode choisi. La fenêtre reste toujours visible par-dessus vos autres applications.

### 2 — Le mini-serveur local

En parallèle, StrangeCat Monitor ouvre un petit serveur web **uniquement accessible depuis votre propre machine** sur le port **5100**. Ce serveur répond à une seule adresse : `http://127.0.0.1:5100/performance`, et renvoie les dernières mesures au format JSON.

### Pourquoi c'est utile pour Wallpaper Engine

Les wallpapers web de Wallpaper Engine sont des pages HTML/JavaScript qui tournent dans un navigateur embarqué. Ce navigateur peut faire des requêtes réseau vers `localhost`, ce qui lui permet d'interroger StrangeCat Monitor en temps réel. Votre wallpaper lit les données JSON, et met à jour ses jauges, graphiques ou textes dynamiquement — tant que StrangeCat Monitor tourne en arrière-plan.

```
  Votre PC                           Wallpaper Engine
  ──────────────────────────────     ─────────────────────────────
  StrangeCat Monitor                 Wallpaper web (HTML/JS)
      │                                    │
      │  collecte CPU/RAM/GPU/NET          │
      │  toutes les 2 secondes             │
      │                                    │  fetch("http://127.0.0.1:5100/performance")
      │◄───────────────────────────────────│
      │                                    │
      │──── répond en JSON ───────────────►│
                                           │  met à jour les jauges du wallpaper
```

> StrangeCat Monitor doit être **lancé avant Wallpaper Engine** (ou au démarrage de Windows) pour que le wallpaper reçoive les données. Si le monitor n'est pas actif, le wallpaper peut afficher des valeurs par défaut ou "--".

---

## Fonctionnalités

- **Widget flottant** — fenêtre sans bordure, toujours au-dessus, transparence réglable
- **Mode Graph** — grille responsive de sparklines (1 à 3 colonnes selon la largeur), chaque métrique collapsible
- **Mode Compact** — barres horizontales ultra-légères, hauteur auto
- **Resize libre** — coin SE, largeur et hauteur ; tout le contenu se rescale proportionnellement
- **Serveur HTTP local** — endpoint JSON sur le port **5100** pour Wallpaper Engine
- **Métriques collectées** :
  - CPU usage & température
  - RAM usage
  - GPU usage & température (NVIDIA via `nvidia-smi`)
  - VRAM usage
  - Vitesse réseau montante et descendante
- **Détection auto de la temp CPU** — 5 méthodes par ordre de priorité
- **Low Power Mode** — refresh ralenti quand la fenêtre est cachée, skip du dessin
- **Tray icon** — Show / Hide / Settings / Quit
- **Démarrage automatique** — option dans les paramètres (registre Windows)
- **Config persistante** — `%APPDATA%\StrangeCat\config.json`

---

## Installation rapide

### Prérequis

```
Python 3.10+   (https://www.python.org/)
```

### Dépendances Python

```bat
pip install psutil pillow pystray pywin32 wmi
```

### Lancer l'application

```bat
python make_icon.py           (une seule fois, génère icon.ico)
python strangecat_monitor.py
```

> Pour avoir la **température CPU** sous Windows, installez
> [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)
> et lancez-le **en Administrateur** avant de démarrer StrangeCat Monitor.

---

## Créer un EXE standalone

Double-cliquez `build.bat` (PyInstaller requis : `pip install pyinstaller`).

L'exécutable est généré dans `dist\StrangeCat Monitor.exe`.
Il peut être placé n'importe où et lancé sans Python installé.

---

## Interface

```
┌──────────────────────────────────────────────────────┐  ← ligne accent rouge
│ 🐱 STRANGECAT          [⊟] [⚙] [—] [✕]             │  ← titlebar (drag)
│    MONITOR  v3.2                                     │
├──────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ ▾ CPU     40%│  │ ▾ RAM     51%│  │ ▾ GPU      │  │  ← grille graph
│  │ ─────────────│  │ ─────────────│  │ ───────────│  │    responsive
│  │  ∿∿∿∿∿∿∿∿∿∿● │  │ ▬▬▬▬▬▬▬▬▬▬●│  │ ∿∿∿∿∿∿∿∿● │  │    1-3 colonnes
│  └──────────────┘  └──────────────┘  └────────────┘  │
│  ... (GPU TEMP · VRAM · NET↓ · NET↑)                  │
├──────────────────────────────────────────────────────┤
│ src: LibreHardwareMonitor   14:32:07    ● :5100   ◢  │  ← footer
└──────────────────────────────────────────────────────┘  ← ligne accent rouge
```

**Boutons de la titlebar :**

| Bouton | Action |
|--------|--------|
| `⊟` / `⊞` | Basculer mode Compact / Graph |
| `⚙` | Ouvrir les paramètres |
| `—` | Réduire dans le tray |
| `✕` | Quitter |

**Footer (bas de fenêtre) :**
- Gauche : source de température CPU active
- Centre : heure courante (mise à jour en temps réel)
- Droite : `● :5100` = serveur actif · `○ off` = désactivé

---

## Sources de température CPU

StrangeCat Monitor essaie les méthodes suivantes dans l'ordre, et utilise la première qui retourne une valeur valide :

| Priorité | Source | Pré-requis |
|----------|--------|-----------|
| 1 | `psutil` | Aucun (fonctionne sur Linux / certains OEM Windows) |
| 2 | WMI `AcpiThermal` | Aucun (ACPI BIOS, variable selon les machines) |
| 3 | WMI `PerfData` | Aucun (compteurs Windows) |
| 4 | **LibreHardwareMonitor** / OpenHardwareMonitor | App tierce lancée en Administrateur ✓ |
| 5 | **CoreTemp** | App tierce avec mémoire partagée active |

**Recommandation Windows :** installer [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) et le lancer en Administrateur au démarrage. C'est la source la plus fiable sur la majorité des configurations.

La source active est visible dans le **footer** de la fenêtre et dans le champ `cpu_temp_method` de l'API.

---

## API HTTP — Wallpaper Engine

Le serveur HTTP démarre automatiquement sur :

```
http://127.0.0.1:5100/performance
```

> **Port par défaut : 5100.** Modifiable dans Settings → HTTP API.

### Réponse JSON

```json
{
  "timestamp": 1767331384.18,
  "psutil": {
    "cpu":              40.0,
    "memory":           51.2,
    "memory_gb":        "8.2GB/16.0GB",
    "gpu_usage":        22.0,
    "gpu_temp":         41.0,
    "vram_usage":       12.0,
    "vram_gb":          "1.5GB/12.0GB",
    "cpu_temp":         58.5,
    "cpu_temp_method":  "LibreHardwareMonitor",
    "upload_speed":     12.4,
    "download_speed":   340.1,
    "timestamp":        1767331384.18
  }
}
```

### Référence des champs

| Clé | Description | Unité |
|-----|-------------|-------|
| `cpu` | Usage CPU global | % |
| `memory` | Usage RAM | % |
| `memory_gb` | RAM utilisée / totale | GB |
| `gpu_usage` | Usage GPU (NVIDIA) | % |
| `gpu_temp` | Température GPU | °C |
| `vram_usage` | Usage VRAM | % |
| `vram_gb` | VRAM utilisée / totale | GB |
| `cpu_temp` | Température CPU (`null` si indisponible) | °C |
| `cpu_temp_method` | Source utilisée pour la temp CPU | string |
| `upload_speed` | Débit réseau montant | KB/s |
| `download_speed` | Débit réseau descendant | KB/s |
| `timestamp` | Timestamp UNIX de la mesure | s |

---

## Intégrer les données dans un wallpaper

Exemple JavaScript complet pour un wallpaper web Wallpaper Engine :

```javascript
const STRANGECAT_PORT = 5100; // Port StrangeCat Monitor (défaut)

async function fetchPerformance() {
  try {
    const response = await fetch(`http://127.0.0.1:${STRANGECAT_PORT}/performance`);
    if (!response.ok) throw new Error("StrangeCat Monitor non disponible");

    const data = await response.json();
    const ps = data.psutil ?? {};

    updateBar("cpu",      ps.cpu,       "%");
    updateBar("ram",      ps.memory,    "%");
    updateBar("gpu",      ps.gpu_usage, "%");
    updateBar("vram",     ps.vram_usage,"%");

    updateText("gpu-temp",  ps.gpu_temp  != null ? `${ps.gpu_temp} °C`  : "—");
    updateText("cpu-temp",  ps.cpu_temp  != null ? `${ps.cpu_temp} °C`  : "—");
    updateText("net-down",  formatSpeed(ps.download_speed));
    updateText("net-up",    formatSpeed(ps.upload_speed));

  } catch (err) {
    // StrangeCat Monitor non lancé : afficher état hors ligne
    showOfflineState();
  }
}

function formatSpeed(kbps) {
  if (kbps == null) return "—";
  if (kbps >= 1024) return `${(kbps / 1024).toFixed(1)} MB/s`;
  return `${kbps.toFixed(0)} KB/s`;
}

// Sync avec le refresh_rate par défaut (2s)
setInterval(fetchPerformance, 2000);
fetchPerformance();
```

> **CORS :** le serveur inclut `Access-Control-Allow-Origin: *` — aucune configuration supplémentaire requise dans Wallpaper Engine.

---

## Wallpapers compatibles

Les wallpapers suivants sont conçus pour fonctionner avec StrangeCat Monitor sur le port **5100** :

> *Aucun wallpaper répertorié pour l'instant. Si vous créez un wallpaper compatible, ouvrez une issue ou une PR pour l'ajouter ici.*

Pour créer un wallpaper compatible, il suffit de faire un `fetch` sur `http://127.0.0.1:5100/performance` et de lire les champs `psutil`. Voir l'[exemple ci-dessus](#intégrer-les-données-dans-un-wallpaper).

---

## Configuration

Les paramètres sont accessibles via le bouton `⚙` de la titlebar.
Le fichier de configuration est enregistré dans :

```
%APPDATA%\StrangeCat\config.json
```

### Paramètres disponibles

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `start_on_boot` | `false` | Démarrage automatique avec Windows |
| `start_minimized` | `false` | Démarrer réduit dans le tray |
| `always_on_top` | `true` | Fenêtre toujours au-dessus |
| `opacity` | `0.96` | Transparence (0.3 → 1.0) |
| `refresh_rate` | `2` | Intervalle de refresh (secondes) |
| `compact_mode` | `false` | Mode compact (barres) ou graph (sparklines) |
| `temp_unit` | `"C"` | Unité de température (`"C"` ou `"F"`) |
| `low_power_mode` | `true` | Ralentit le refresh quand la fenêtre est cachée |
| `http_enabled` | `true` | Activer le serveur HTTP |
| `http_port` | `5100` | Port du serveur HTTP |
| `window_width` | `380` | Largeur initiale de la fenêtre (px) |
| `show_cpu` | `true` | Afficher CPU usage |
| `show_cpu_temp` | `true` | Afficher CPU température |
| `show_ram` | `true` | Afficher RAM |
| `show_gpu` | `true` | Afficher GPU usage |
| `show_gpu_temp` | `true` | Afficher GPU température |
| `show_vram` | `true` | Afficher VRAM |
| `show_net` | `true` | Afficher réseau ↓↑ |

---

## Résolution de problèmes

### 🌡️ La température CPU affiche "N/A"

**Cause :** Windows ne donne pas accès aux capteurs thermiques sans application tierce sur la plupart des configurations.

**Solutions, dans l'ordre :**
1. Installez [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)
2. Lancez-le **en Administrateur** (clic droit → Exécuter en tant qu'administrateur)
3. Laissez-le tourner en arrière-plan (il peut être minimisé dans le tray)
4. Relancez StrangeCat Monitor — la source devrait passer à `LibreHardwareMonitor`

> Vous pouvez aussi essayer [CoreTemp](https://www.alcpu.com/CoreTemp/) si LibreHardwareMonitor ne fonctionne pas sur votre machine.

---

### 📊 Le wallpaper n'affiche pas les données / affiche "--"

**Cause :** Le wallpaper ne peut pas joindre le serveur StrangeCat Monitor.

**Vérifications :**
1. **StrangeCat Monitor est-il lancé ?** — Vérifiez la barre des tâches ou le tray (icône 🐱). Si non, lancez-le.
2. **Le serveur HTTP est-il actif ?** — Le footer doit afficher `● :5100`. Si c'est `○ off`, allez dans Settings → HTTP API et activez le serveur.
3. **Le port est-il le bon ?** — Vérifiez que votre wallpaper utilise bien le port `5100`. Certains wallpapers utilisent le port `5000` (PerformanceMonitor de sheetau) — ils ne sont pas directement compatibles sans modification.
4. **Testez manuellement** — Ouvrez un navigateur et allez sur `http://127.0.0.1:5100/performance`. Si vous voyez du JSON, le serveur fonctionne correctement.

---

### 🔴 Le port 5100 est déjà utilisé

**Symptôme :** Le footer affiche `○ off` même avec le serveur activé, ou une erreur apparaît au démarrage.

**Solution :**
1. Allez dans Settings → HTTP API
2. Changez le port (ex. `5101`, `5200`, `8080`)
3. Cliquez SAVE — le serveur redémarre automatiquement sur le nouveau port
4. Mettez à jour le port dans vos wallpapers en conséquence

> Pour vérifier quel programme utilise le port 5100 : ouvrez un terminal et tapez `netstat -ano | findstr :5100`

---

### 🎮 GPU affiche 0 % ou pas de données

**Cause :** StrangeCat Monitor utilise `nvidia-smi` pour interroger le GPU — uniquement disponible sur les cartes NVIDIA.

**AMD / Intel :** Les données GPU ne sont pas supportées pour le moment. Les métriques GPU resteront à 0 ou N/A. Seuls CPU, RAM et réseau seront disponibles.

**NVIDIA — `nvidia-smi` introuvable :**
- Vérifiez que les drivers NVIDIA sont installés
- Ouvrez un terminal et tapez `nvidia-smi` — si la commande est inconnue, réinstallez les drivers depuis [nvidia.com](https://www.nvidia.com/Download/index.aspx)

---

### 🪟 La fenêtre a disparu / est hors écran

**Cause :** La fenêtre a été déplacée hors des limites de l'écran (ex. après un changement de résolution ou de configuration multi-moniteurs).

**Solution :**
1. Clic droit sur l'icône tray → **Show**
2. Si la fenêtre n'apparaît pas à l'écran, éditez manuellement la config :
   - Ouvrez `%APPDATA%\StrangeCat\config.json`
   - Remettez `pos_x` et `pos_y` à des valeurs valides (ex. `100`, `100`)
   - Sauvegardez et relancez

---

### ⚡ L'application consomme trop de ressources

**Solutions :**
- Activez **Low Power Mode** dans Settings → Display (coché par défaut)
- Augmentez le **Refresh Rate** à 5 secondes dans Settings → Display
- Passez en **mode Compact** (bouton `⊟` dans la titlebar) — moins de calculs graphiques
- Réduisez la fenêtre dans le tray (`—`) quand vous n'en avez pas besoin — le refresh se ralentit automatiquement

---

### 🔄 L'application ne démarre pas au boot malgré l'option activée

**Cause :** Le raccourci de démarrage nécessite des droits d'écriture dans le registre.

**Solution :**
1. Lancez StrangeCat Monitor **en Administrateur** une fois
2. Allez dans Settings → System → "Start on boot" → activez et sauvegardez
3. Les lancements suivants n'auront plus besoin des droits admin

---

### 🗑️ Réinitialiser la configuration

Supprimez le fichier de config et l'application repartira avec les valeurs par défaut :

```
%APPDATA%\StrangeCat\config.json
```

---

## Sécurité & vie privée

- Fonctionne **entièrement en local** — aucune donnée envoyée sur internet
- Le serveur HTTP n'écoute que sur `127.0.0.1` (votre machine uniquement, inaccessible depuis le réseau)
- Aucune télémétrie, aucun tracking, aucun compte requis
- Code source entièrement lisible et modifiable
- La configuration est stockée localement dans `%APPDATA%\StrangeCat\`

---

## Dépendances

| Bibliothèque | Usage |
|-------------|-------|
| [psutil](https://github.com/giampaolo/psutil) | CPU, RAM, réseau |
| [Pillow](https://python-pillow.org/) | Génération de l'icône tray |
| [pystray](https://github.com/moses-palmer/pystray) | Icône systray Windows |
| [pywin32](https://github.com/mhammond/pywin32) | Registre Windows (démarrage auto) |
| [wmi](https://pypi.org/project/WMI/) | Température CPU via WMI / LibreHardwareMonitor |
| `nvidia-smi` | GPU NVIDIA (inclus dans les drivers NVIDIA) |
| [Wallpaper Engine](https://www.wallpaperengine.io/) | Client wallpaper cible |

---

## Historique des versions

### v3.2 — Rendu & Grid
- **Footer** déplacé en bas : source temp · heure · statut HTTP
- **Grid responsive** réécrite — layout natif Tkinter, cellules égales (uniform), sans Canvas ni Scrollbar
- **Palette** affinée (plus sombre, plus contrastée)
- Valeurs affichées en vert, halo sur les dots de graphiques
- Mode graph : hauteur initiale correcte (420px) au basculement depuis compact

### v3.1 — Mode Graph
- Première implémentation de la grille responsive
- Footer agrandi, boutons plus grands
- Low Power Mode, cache GPU (2s TTL)
- Refresh rate par défaut augmenté (1→2s)

### v2.2 — Stabilité
- Crash CoreTemp résolu (mémoire partagée sécurisée)
- Settings : Save fiable, config dans `%APPDATA%`
- Resize 8 directions

### v1.0 — Initial
- Widget flottant, mode compact, API HTTP
