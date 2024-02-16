# rosinenpicker

![Python Packaging](https://github.com/joheli/rosinenpicker/workflows/Packaging/badge.svg) ![PyPI](https://img.shields.io/pypi/v/rosinenpicker?label=PyPI) ![PyPI - Downloads](https://img.shields.io/pypi/dm/rosinenpicker)

[English](README.md)

# Handbuch

Willkommen bei `rosinenpicker`! Dieses Werkzeug ist wie ein magisches Sieb, das Ihnen hilft, goldene Informationsnuggets (oder "Rosinen") in einem Berg von Dokumenten zu finden. Es ist für jeden gedacht, der spezifische Informationen extrahieren muss, ohne sich in technische Details zu vertiefen.

## Schlüsselbegriffe verstehen

- **Kommandozeile**: Eine textbasierte Schnittstelle, um Ihren Computer zu bedienen. Stellen Sie sich vor, Ihrem Computer genau zu sagen, was er tun soll, indem Sie Befehle eingeben.
- **YAML**: Ein einfaches Konfigurationsdateiformat, das von `rosinenpicker` verwendet wird, um Ihre Anweisungen zu verstehen. Es ist leicht zu lesen und zu schreiben.
- **Argumente**: Spezielle Anweisungen, die Sie `rosinenpicker` beim Start geben, um ihm zu sagen, wo es seine Anweisungen (YAML-Datei) finden und wo es seine Funde speichern soll.

## Erste Schritte

0. **Python 3.11 ist Voraussetzung**: Stellen Sie sicher, dass Python 3.11 oder höher installiert ist. Es gibt viele Wege um Python zu installieren, aber ich empfehle[Miniconda](https://docs.anaconda.com/free/miniconda/index.html).

1. **Installation**: Zuerst bringen wir `rosinenpicker` auf Ihren Computer. Öffnen Sie Ihre Kommandozeile und tippen Sie:

   ```
   pip install rosinenpicker
   ```

2. **Das Programm ausführen**: Um `rosinenpicker` zu starten, geben Sie folgendes ein:

   ```
   rosinenpicker -c pfad/zu/ihrem_config.yml -d pfad/zu/ihrer_datenbank.db
   ```

   Ersetzen Sie `pfad/zu/ihrem_config.yml` mit dem tatsächlichen Pfad zu Ihrer Konfigurationsdatei und `pfad/zu/ihrer_datenbank.db` mit dem Ort, an dem Sie die Funde speichern möchten. (Wenn nicht anders angegeben, wird davon ausgegangen, dass die Konfigurations- und Datenbankdateien `config.yml` und `matches.db` in Ihrem aktuellen Verzeichnis sind; außerdem wird die Datenbank automatisch erstellt, wenn sie nicht auf Ihrem System vorhanden ist.)

## Ihre YAML-Konfiguration erstellen

Hier ist eine Beispielkonfiguration, die `rosinenpicker` leitet:

```yaml
title: 'Meine Dokumentsuche'
strategies:
  strategy1:
    processed_directory: '/pfad/zu/dokumenten'
    file_name_pattern: '.*\.pdf'
    file_format: 'pdf'
    terms:
      term1: 'Apfelkuchen'
    export_format: 'csv'
    export_path: '/pfad/zu/export.csv'
```

Dies sagt `rosinenpicker`, in `/pfad/zu/dokumenten` nach PDF-Dateien zu suchen, die "Apfelkuchen" enthalten, und die Ergebnisse in einer CSV-Datei unter `/pfad/zu/export.csv` zu speichern. Weitere Informationen finden Sie in der [Beispielkonfigurationsdatei](configs/config.yml) in diesem Repository - die Datei enthält zusätzliche Kommentare, die Sie nützlich finden könnten.

### Weitere Möglichkeiten

Nun ist es natürlich nicht sehr nützlich, nur den Begriff "Apfelkuchen" aus Dokumenten zu extrahieren. Aber Sie können viel mehr tun. Anstelle von "Apfelkuchen" können Sie einen regulären Ausdruck eingeben, z. B. "\d{8}", um Zahlen zu extrahieren, die aus genau acht Ziffern bestehen. Aber es gibt noch mehr: Wenn Sie einen Ausdruck zusammen mit "@@@" (was für "variable Zeichenfolge" steht) eingeben, wird nur eine Übereinstimmung mit "@@@" zurückgegeben. Z.B. "Name: @@@" wird alles zurückgeben, was auf "Name:" folgt!

## `rosinenpicker` verwenden

Mit Ihrer fertigen `config.yml` kehren Sie zur Kommandozeile zurück und führen `rosinenpicker` mit den Argumenten `-c` und `-d` wie oben gezeigt aus.

## Hilfe und Optionen

Für eine Liste der Befehle und Optionen tippen Sie:

```
rosinenpicker -h
```

Dieser Befehl zeigt alles an, was Sie wissen müssen, um `rosinenpicker` zu navigieren.

## Schlussfolgerung

Sie sind jetzt bereit, mit `rosinenpicker` wertvolle Informationen zu erkunden und zu extrahieren. Viel Erfolg bei der Informationssuche!
