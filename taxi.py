import csv
from random import choice, uniform
from datetime import datetime, timedelta

# Coordonnées approximatives de la région d'Alger
MIN_LAT = 36.6
MAX_LAT = 36.9
MIN_LON = 3.0
MAX_LON = 3.3

# Noms des chauffeurs
drivers = ['d1', 'd2', 'd3', 'd4', 'd5']

# Localités de la région d'Alger
locations = [
    ("El Biar", 36.7867, 3.0517),
    ("Hussein Dey", 36.7367, 3.0867),
    ("Bab El Oued", 36.7167, 3.1267),
    ("Bir Mourad Rais", 36.7417, 3.1517),
    ("Bouzareah", 36.7717, 3.0317),
    ("Cheraga", 36.6617, 3.2167),
    ("Dely Ibrahim", 36.6867, 3.0667),
    ("Draria", 36.6867, 3.2867),
    ("El Harrach", 36.7167, 3.1517),
    ("Mohammadia", 36.7917, 3.0667)
]

# Date et heure de début
start_datetime = datetime(2024, 3, 6, 13, 0)

# Générer les données
data = []
for driver in drivers:
    for hour in range(0, 13, 3):
        row = []
        current_datetime = start_datetime + timedelta(hours=hour)
        row.append(current_datetime.strftime('%m/%d/%Y-%I:%M:%S %p'))  # Time et Date
        latitude = uniform(MIN_LAT, MAX_LAT)
        longitude = uniform(MIN_LON, MAX_LON)
        row.append(latitude)  # Latitude
        row.append(longitude)  # Longitude
        row.append(driver)  # Driver
        row.append(choice(['TRUE', 'FALSE']))  # disponible
        row.append(choice(['TRUE', 'FALSE']))  # accepte
        
        # Trouver la localité correspondante
        location = None
        min_distance = float('inf')
        for loc_name, loc_lat, loc_lon in locations:
            distance = ((latitude - loc_lat) ** 2 + (longitude - loc_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                location = loc_name
        row.append(location)
        
        data.append(row)

# Écrire les données dans un fichier CSV
with open('alger_taxis.csv', 'w', newline='') as csvfile:
    fieldnames = ['Time et Date', 'Latitude', 'Longitude', 'Driver', 'disponible', 'accepte', 'Location']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in data:
        writer.writerow({'Time et Date': row[0], 'Latitude': row[1], 'Longitude': row[2], 'Driver': row[3], 'disponible': row[4], 'accepte': row[5], 'Location': row[6]})

print("Le fichier 'alger_taxis.csv' a été généré avec succès.")