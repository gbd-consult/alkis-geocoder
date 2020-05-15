ALKIS-Geocoder
==============

Geokodierung von Adressdaten auf Basis von ALKIS
------------------------------------------------

Dieses Plugin ermöglicht die Zuordnung von Geokodierungen zu Adressdaten auf Basis von ALKIS Daten.
So können für beliebige Adressen lat und lon Werte schnell gefunden und zugeordnet werden.
Durch eine Authentifizierung per User und Passwort, kann diese Funktion nur für verifizierte Nutzer bereitgestellt werden.
Dazu wird eine Schnitstelle zur GBD WebSuite genutzt.

<img src="/images/geocoder_blank.png" width="300">


Installation
------------

Das Plugin wird über das [Plugin Repository der Geoinformatikbüro Dassau GmbH](https://plugins.gbd-consult.de) bereitgestellt. Sie können das Repository über den QGIS Pluginmanager einbinden.

<img src="/images/repodetails.png" width="300">

Das Plugin kann über das Menü Erweiterungen -> GBD ALKIS Geocoder geladen werden.


Bedienung
---------
Wenn Sie den GBD ALKIS Geocoder geöffnet haben, finden Sie folgendes Fenster vor:

<img src="/images/geocoder_blank.png" width="300">

Zuerst müssen Sie eine URL eintragen die Ihnen Zugriff auf die GBD Websuite API ermöglicht.
## Muss diese vorher bei uns angelegt oder angefragt werden? Woher bekommt man diese?
Wenn Sie die URL eingetragen haben, schaut das Plugin ob für diese eine Authentifizierung per Benutzer und Passwort nötig ist.
Falls ja, tragen Sie einen für diese URL verifizierten Benutzer mit Passwort ein.
Dann muss die Auswahl einer in QGIS bereits geladenen Tabelle mit Adressdaten und korrekter Schriftkodierung erfolgen.
## Output Daten mit Gemarkung etc. oder Input Daten mit Gemarkung etc.. Wenn zweiteres was ist dann die Geokodierung?
Jetzt müssen Sie noch die Spalten Gemarkung, Straße und Hausnummer  manuell zuweisen.
Über den Button 'Layer generieren' starten Sie die Geokodierung.
Nun wird ein neuer Punktlayer mit lat und lon werten generiert.

<img src="/images/geocoder_filled.png" width="300">

Das Plugin wurde zuletzt im April 2020 aktualisiert.

## Lizenz

Dieses Programm ist freie Software. Es kann unter der den Bedingungen der [GNU General Public License](./LICENSE) weitergegeben und/oder verändert werden. Entweder unter der Version 2 oder einer späteren Version der GPL.
