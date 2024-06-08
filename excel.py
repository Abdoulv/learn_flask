import openpyxl
import mysql.connector

# Connexion à la base de données MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="login_register_db"
)

mycursor = mydb.cursor()

# Chemin vers le fichier Excel
excel_file = 'test.xlsx'

# Ouverture du fichier Excel
workbook = openpyxl.load_workbook(excel_file)

# Sélection de la première feuille
sheet = workbook.active

# Boucle sur les lignes du fichier Excel à partir de la deuxième ligne (après l'en-tête)
for row in sheet.iter_rows(min_row=2, values_only=True):
    time_date = row[0]
    latitude = row[1]
    longitude = row[2]
    driver = row[3]

    # Requête SQL pour insérer les données dans la table driver_location
    sql = "INSERT INTO driver_location (time_date, latitude, longitude, driver) VALUES (%s, %s, %s, %s)"

    # Valeurs à insérer dans la table
    values = (time_date, latitude, longitude, driver)

    try:
        # Exécuter la requête SQL
        mycursor.execute(sql, values)
        # Valider la transaction
        mydb.commit()
        print("Données insérées avec succès.")
    except Exception as e:
        # En cas d'erreur, annuler la transaction
        mydb.rollback()
        print(f"Erreur lors de l'insertion des données : {e}")

# Fermer le curseur et la connexion à la base de données
mycursor.close()
mydb.close()
