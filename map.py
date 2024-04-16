from arcgis.gis import GIS

gis = GIS("https://www.arcgis.com", "matteo.donaggio_serendpt", "Mobi80100")
# Ottieni la mappa utilizzando l'ID mappa
mappa = gis.content.get("5ae37f33f52a4eefbc098507ddd9f92d")

# Supponendo che tu abbia una lista di dizionari con i dati delle chiese
# ogni elemento della lista ha latitudine, longitudine, nome, e altri dettagli
chiese_data = [{"latitude": 45.4375, "longitude": 12.3358, "nome": "Chiesa di Venezia", "dettagli": "Alcuni dettagli qui"}]

# Qui dovresti convertire i tuoi dati in un formato compatibile con ArcGIS, come un FeatureCollection o simile
# Questo dipende dalla struttura dei tuoi dati e da come desideri visualizzarli sulla mappa
