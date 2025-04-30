import subprocess
import shutil

# Installation unter Windows (auch als Portable-Version unter https://gnuwin32.sourceforge.net/packages/wget.htm

# Ziel-URL
url = "http://suprasliensis.obdurodon.org/"

# Der genaue wget-Befehl als Liste
wget_command = [
    "wget",
    "--no-check-certificate",        # ignoriert ungültige SSL-Zertifikate (nicht nötig für HTTP, aber sicherheitshalber dabei)
    "-e", "robots=off",              # ignoriert robots.txt (für vollständiges Harvesting notwendig)
    "-r",                            # rekursiv
    "--no-parent",                   # keine übergeordnete Verzeichnisse
    "-k",                            # konvertiert Links zur Offline-Nutzung
    "-E",                            # fügt .html-Endung hinzu
    "-A", "html",                    # lädt nur HTML-Dateien
    url
]

def main():
    if not shutil.which("wget"):
        print("Fehler: wget ist nicht installiert oder nicht im PATH.")
        print("Bitte installiere wget manuell oder lege wget.exe in dieses Verzeichnis.")
        return

    print("Starte den Download mit wget...\n")
    try:
        subprocess.run(wget_command, check=True)
        print("\nDownload abgeschlossen.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von wget:\n{e}")
    except Exception as e:
        print(f"Unerwarteter Fehler:\n{e}")

if __name__ == "__main__":
    main()