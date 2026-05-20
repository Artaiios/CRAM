# CRAM — Server-Setup für Online-Sync

CRAM nutzt für den Online-Sync (V1.2/V1.3 manuell, ab V2.0 zusätzlich automatisch) ein **statisches HTTP-Backend**, das `GET`, `HEAD`, `PUT` und `OPTIONS` auf einem einzigen Endpunkt (`/cram/state.json` o.ä.) entgegennimmt und CORS-Anfragen vom Browser akzeptiert. Es gibt keine CRAM-spezifische Server-Software — jeder generische Webserver mit WebDAV-Methoden tut es.

Dieses Dokument zeigt Referenz-Konfigurationen für die häufigsten Server-Optionen. Wähle eine aus, passe die Pfade an und folge der CORS-Sektion.

## Inhaltsübersicht

- [Was der Server tatsächlich tun muss](#was-der-server-tatsaechlich-tun-muss)
- [Variante A: nginx mit `dav_methods`](#variante-a-nginx-mit-dav_methods)
- [Variante B: Caddy mit `webdav`-Plugin](#variante-b-caddy-mit-webdav-plugin)
- [Variante C: Apache mit `mod_dav`](#variante-c-apache-mit-mod_dav)
- [Variante D: MinIO mit presigned URLs (Vorausschau auf V2.1)](#variante-d-minio-mit-presigned-urls)
- [CORS-Anforderungen](#cors-anforderungen)
- [Authentifizierung](#authentifizierung)
- [TLS / HTTPS](#tls--https)
- [Skalierungs-Erwartungen](#skalierungs-erwartungen)
- [Lokales Dev-Backend (eingebaut)](#lokales-dev-backend-eingebaut)

## Was der Server tatsächlich tun muss

CRAM erwartet eine URL wie `https://crisis.example.com/cram/state.json`, auf der:

| HTTP-Methode | Erwartetes Verhalten |
|---|---|
| `GET` | Liefert den zuletzt geschriebenen JSON-Inhalt mit Status 200, oder 404 wenn noch nie etwas geschrieben wurde |
| `HEAD` | Wie `GET` ohne Body — Last-Modified / ETag liefern |
| `PUT` | Speichert den Request-Body unter dieser URL, Status 200/201/204 |
| `OPTIONS` | CORS-Preflight für die o.g. Methoden, Status 204 |

Der Body ist immer ein JSON-Objekt, dessen Struktur CRAM selbst kennt (`format: "cram-sync-v1"`). Der Server muss den Inhalt nicht inspizieren — er ist ein opaker Storage.

**Wichtig:** keine Indizierung, kein Listing, kein automatisches Backup-Rotieren des Server-Verzeichnisses durch andere Prozesse. CRAM überschreibt die Datei bei jedem Push komplett.

### Zusätzliche Anforderungen für V2.0-Auto-Sync

Auto-Sync (V2.0) funktioniert ohne Konfliktbehandlung gegen jeden Server, der die Tabelle oben erfüllt. Für **Lost-Update-Schutz** bei parallelen Editoren braucht es zwei zusätzliche Eigenschaften:

| Eigenschaft | Wozu | Wer liefert |
|---|---|---|
| `ETag`-Response-Header auf `GET`/`HEAD`/`PUT`-Responses | CRAM merkt sich den letzten ETag pro Source | Server muss ihn setzen |
| `If-Match`-Validation auf `PUT` | Server lehnt mit **412 Precondition Failed** ab, wenn ein anderer Schreiber zwischenzeitlich den Inhalt geändert hat | Server validiert das vor dem Schreiben |

**Verhalten ohne ETag-Support:** CRAM funktioniert weiter, aber bei zwei parallelen Schreibern kann der spätere Push den früheren stillschweigend überschreiben. Die Audit-Log-Einträge bleiben erhalten (siehe Auto-Sync-Doku im Handbuch), der Status-Wert geht aber verloren. Akzeptable Trade-off für Setups mit wenigen Editoren oder strenger organisatorischer Schreib-Disziplin.

**nginx**, **Apache** und **Caddy mit `caddy-webdav`** setzen ETags automatisch und respektieren `If-Match` ohne weitere Konfiguration — die Beispiele unten sind aus diesem Grund bereits V2.0-tauglich. **MinIO** und **S3-kompatible Backends** setzen ebenfalls ETags (über den Object-MD5). Reine statische Hoster ohne Conditional-Request-Support (manche CDN-Edges, simple Python-`http.server`-Setups) funktionieren technisch, bieten aber keinen Lost-Update-Schutz.

Die CORS-Allow-Headers in allen Beispielen unten enthalten bereits `If-Match` und `If-None-Match`; die Expose-Headers `ETag` und `Last-Modified`. Das ist V1.2-Boilerplate, das V2.0 jetzt aktiv benutzt.

## Variante A: nginx mit `dav_methods`

nginx kann ab Werk `PUT` und `DELETE` (Modul `ngx_http_dav_module`, in allen offiziellen Builds dabei). Voll funktionierende Reference-Config:

```nginx
server {
    listen 443 ssl http2;
    server_name crisis.example.com;

    ssl_certificate     /etc/letsencrypt/live/crisis.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/crisis.example.com/privkey.pem;

    location /cram/ {
        root /var/www;            # die Datei landet unter /var/www/cram/state.json
        client_body_temp_path /var/cache/nginx/dav-tmp;
        create_full_put_path on;
        dav_methods PUT DELETE;
        dav_access user:rw group:rw all:r;
        client_max_body_size 5m;  # Reserve für sehr große Stäbe + verschlüsseltes Envelope

        # ---- Auth (Basic) ----
        auth_basic           "CRAM Sync";
        auth_basic_user_file /etc/nginx/.htpasswd-cram;

        # ---- CORS ----
        add_header Access-Control-Allow-Origin  "*" always;
        add_header Access-Control-Allow-Methods "GET, HEAD, PUT, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, If-Match, If-None-Match" always;
        add_header Access-Control-Expose-Headers "ETag, Last-Modified" always;
        add_header Access-Control-Max-Age       "86400" always;

        # OPTIONS-Preflight direkt beantworten, ohne weitere Verarbeitung
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
}
```

Schritte:
1. `htpasswd -c /etc/nginx/.htpasswd-cram cram-user` — Passwort vergeben
2. `mkdir -p /var/www/cram /var/cache/nginx/dav-tmp && chown -R www-data:www-data /var/www/cram /var/cache/nginx/dav-tmp`
3. nginx-Config testen + neu laden: `nginx -t && systemctl reload nginx`
4. Smoketest:
   ```bash
   curl -u cram-user:secret -X PUT --data '{"format":"cram-sync-v1","version":1,"timestamp":1,"fingerprint":"AAAA","encrypted":false,"payload":{}}' \
        -H "Content-Type: application/json" https://crisis.example.com/cram/state.json
   curl -u cram-user:secret https://crisis.example.com/cram/state.json
   ```

## Variante B: Caddy mit `webdav`-Plugin

Caddy hat `PUT` nicht im Default-Build. Das Community-Plugin [`caddy-webdav`](https://github.com/mholt/caddy-webdav) liefert es nach.

Caddy mit dem Plugin neu bauen:

```bash
xcaddy build --with github.com/mholt/caddy-webdav
```

`Caddyfile`:

```caddyfile
crisis.example.com {
    @cram path /cram/*
    handle @cram {
        # Basic-Auth (Caddy v2.7+ native)
        basicauth /cram/* {
            cram-user <bcrypted-hash>
        }
        webdav {
            root /var/www/cram
        }
        header {
            Access-Control-Allow-Origin  "*"
            Access-Control-Allow-Methods "GET, HEAD, PUT, OPTIONS"
            Access-Control-Allow-Headers "Authorization, Content-Type, If-Match, If-None-Match"
            Access-Control-Expose-Headers "ETag, Last-Modified"
            Access-Control-Max-Age       "86400"
        }
        @options method OPTIONS
        respond @options 204
    }
}
```

`bcrypted-hash` erzeugen: `caddy hash-password --plaintext '<dein-passwort>'`.

## Variante C: Apache mit `mod_dav`

```apache
<VirtualHost *:443>
    ServerName crisis.example.com

    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/crisis.example.com/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/crisis.example.com/privkey.pem

    DocumentRoot /var/www

    <Location /cram>
        DAV on
        AuthType Basic
        AuthName "CRAM Sync"
        AuthUserFile /etc/apache2/.htpasswd-cram
        Require valid-user

        Header always set Access-Control-Allow-Origin  "*"
        Header always set Access-Control-Allow-Methods "GET, HEAD, PUT, OPTIONS"
        Header always set Access-Control-Allow-Headers "Authorization, Content-Type, If-Match, If-None-Match"
        Header always set Access-Control-Expose-Headers "ETag, Last-Modified"
        Header always set Access-Control-Max-Age       "86400"
    </Location>

    <If "%{REQUEST_METHOD} == 'OPTIONS'">
        Header always set Status "204"
    </If>
</VirtualHost>
```

Module aktivieren: `a2enmod dav dav_fs headers ssl && systemctl reload apache2`.

## Variante D: MinIO mit presigned URLs

Volle Integration kommt mit V2.1 (S2-Backend). Bis dahin kann der Pattern dieser Form bereits getestet werden:

1. MinIO-Bucket erzeugen (z.B. `cram-sync`)
2. CORS auf dem Bucket setzen (per `mc admin policy` oder Bucket-Settings)
3. Presigned PUT- und GET-URLs erzeugen (z.B. 7 Tage gültig):
   ```bash
   mc share upload --expire 168h myalias/cram-sync/state.json
   mc share download --expire 168h myalias/cram-sync/state.json
   ```
4. In V1.2 manuell: HTTP-Source mit `authType: none` und der presigned URL anlegen. **Nachteil:** die URL läuft nach 7 Tagen ab und muss erneuert werden. V2.1 löst das mit URL-Rotation.

## CORS-Anforderungen

CRAM läuft aus dem Browser, oft mit anderem Origin als der Sync-Server. Ohne CORS-Header schlägt der Browser jeden Request ab.

Minimaler CORS-Header-Set (auf allen Antworten):

```
Access-Control-Allow-Origin:  *                     # oder spezifischer Origin
Access-Control-Allow-Methods: GET, HEAD, PUT, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, If-Match, If-None-Match
Access-Control-Expose-Headers: ETag, Last-Modified
Access-Control-Max-Age:       86400
```

**Strenger:** Statt `*` den konkreten Origin angeben (z.B. `https://cram.intern.example.com`). Das blockiert andere Webseiten daran, gegen euren Server zu schreiben.

**Preflight (OPTIONS):** muss mit 2xx und den oben genannten Headern antworten. Bei nginx/Apache passiert das automatisch durch die `if`/`<If>`-Blöcke; bei Caddy durch `respond @options 204`.

## Authentifizierung

CRAM unterstützt drei Auth-Typen in V1.2:

| Typ | Wie konfigurieren |
|---|---|
| `none` | keine Auth — nur sinnvoll im VPN/Intranet ohne Internet-Exposure |
| `basic` | Server validiert `Authorization: Basic <base64(user:pass)>` — siehe nginx/Apache/Caddy-Beispiele |
| `bearer` | Server validiert `Authorization: Bearer <token>` — z.B. mit OAuth2-Proxy, statisch in nginx mit `if`, oder app-spezifischer Token-Check |

**Tipp:** für eine reine Stab-interne Lösung reicht `basic` mit einem geteilten Passwort. Das Passwort kommt in das Sync-Bundle, dass per Signal/Threema verteilt wird.

## TLS / HTTPS

CRAM-Browser-Code akzeptiert `https://` (Production) und `http://127.0.0.1:*` (Dev). HTTPS ist Pflicht für alles, was nicht lokal ist — Browser blockieren Mixed-Content und der Sync-Bundle-Inhalt (Passphrase!) darf nicht im Klartext über die Leitung.

Let's-Encrypt-Setup ist Standard-Stoff (`certbot --nginx` o.ä.) und nicht in den Beispielen aufgeführt.

## Skalierungs-Erwartungen

Annahmen für eine typische Stab-Größe (siehe ROADMAP):
- 20–30 Rollen, 50–100 User
- Die meisten User sind Read-Only (Konsumenten)
- ~3–10 aktive Editoren

In V1.2 (manueller Sync): jeder User klickt explizit „Pull" oder „Push". Server-Last sehr gering — wenige Requests pro Stunde.

In V2.0 (automatischer Sync): Polling alle 90 Sek pro User. Bei 100 Usern → ~1 Request/Sekunde im Schnitt. Trivial für jeden der oben genannten Server.

Bei einer Größenordnung darüber (>1000 User, mehrere parallele Stäbe) sollte vor dem Rollout das Backend-Setup mit dem IT-Betrieb abgestimmt werden — z.B. nginx-Caching auf der GET-Route, statt jedesmal die Datei vom Disk zu lesen.

## Lokales Dev-Backend (eingebaut)

Für lokale Tests gibt es im Repo `scripts/dev-sync-backend.py` — pure Python-Stdlib, kein Install nötig:

```bash
python3 scripts/dev-sync-backend.py
# CRAM dev sync backend listening on http://127.0.0.1:8765/cram/state.json
```

Dieses Mini-Backend simuliert das Verhalten der echten Server (GET/HEAD/PUT/OPTIONS mit CORS), schreibt den State in `scripts/dev-sync-state.json` (gitignored) und ist absichtlich **nicht für Production**. Es hat keine Auth, kein TLS, kein Rate-Limiting.

`python3 scripts/dev-sync-backend.py --reset` löscht den State und beendet sich. `--port <N>` setzt einen anderen Port.

**Bekannte Einschränkung (V2.0-rc1):** Das Dev-Backend setzt ETags, validiert `If-Match` aber noch nicht aktiv — ein 412-Pfad lässt sich damit nicht testen. Wer den V2.0-Konfliktpfad gegen einen lokalen Server testen will, sollte stattdessen ein lokales nginx mit der Variante-A-Config aufsetzen. Die fehlende If-Match-Validation im Dev-Backend steht im CHANGELOG unter „Deferred — out of scope for RC1, in scope for RC2 / GA".

---

## Weiteres

- Detail-Spec: [`docs/specs/v1.2-manual-sync.md`](specs/v1.2-manual-sync.md)
- Roadmap: [`ROADMAP.md`](../ROADMAP.md)
- Bei Fragen: GitHub-Issues unter [Artaiios/CRAM](https://github.com/Artaiios/CRAM/issues)
