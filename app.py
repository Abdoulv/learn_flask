from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics import silhouette_score

app = Flask(__name__)
CORS(app, supports_credentials=True)


# Connect to the database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='login_register_db'
)

# Fetch data from the database (assuming 'time_date', 'latitude', and 'longitude' columns)
cursor = conn.cursor()
cursor.execute("SELECT time_date, latitude, longitude, driver_id FROM driver_location")
data = cursor.fetchall()
df = pd.DataFrame(data, columns=['time_date', 'latitude', 'longitude', 'driver_id'])

# Clean column names
df.columns = df.columns.str.strip()

# Convert timestamp strings to datetime objects
df['time_date'] = pd.to_datetime(df['time_date'], format='%d/%m/%Y-%I:%M:%S %p')

# Extract relevant features from the timestamp
df['hour'] = df['time_date'].dt.hour
df['day_of_week'] = df['time_date'].dt.dayofweek

# Combine features for clustering
features = df[['latitude', 'longitude', 'hour', 'day_of_week']].values

# Determine the optimal number of clusters using the silhouette method
silhouette_scores = []
for i in range(2, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    cluster_labels = kmeans.fit_predict(features)
    silhouette_avg = silhouette_score(features, cluster_labels)
    silhouette_scores.append(silhouette_avg)

optimal_clusters_silhouette = np.argmax(silhouette_scores) + 2

# Perform K-Means clustering
kmeans = KMeans(n_clusters=optimal_clusters_silhouette, random_state=42)
kmeans.fit(features)
df['cluster'] = kmeans.predict(features)
cluster_centers = kmeans.cluster_centers_

# Function to find the best cluster for the client
def find_best_cluster(client_lat, client_long):
    distances = np.sqrt((cluster_centers[:, 0] - client_lat)**2 + (cluster_centers[:, 1] - client_long)**2)
    return distances.argsort()

@app.route('/update_driver_availability', methods=['POST'])
def update_driver_availability():
    data = request.get_json()
    driver_id = data['driver_id']
    availability = data['availability']

    # Update driver availability in the database
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE tbl_driver SET available = %s WHERE idd = %s"
            cursor.execute(sql, (availability, driver_id))
        conn.commit()
        return jsonify({'message': 'Driver availability updated successfully.'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Error updating driver availability: {str(e)}'}), 500

# Adjusted find_drivers route
@app.route('/find_drivers', methods=['POST'])
def find_drivers():
    data = request.get_json()
    print(f"Received request with data: {data}")
    client_lat = data['latitude']
    client_long = data['longitude']
    destination = data.get('destination', 'unknown')
    num_places = data['num_places']
    best_clusters = find_best_cluster(client_lat, client_long)
    available_drivers = []

    for cluster_number in best_clusters:
        cluster_drivers = df[df['cluster'] == cluster_number]
        for _, driver in cluster_drivers.iterrows():
            # Fetch driver information from the database including latitude and longitude
            cursor.execute("SELECT d.firstname, dl.latitude, dl.longitude, d.available FROM tbl_driver d JOIN driver_location dl ON d.idd = dl.driver_id WHERE d.idd = %s", (driver['driver_id'],))
            driver_info = cursor.fetchone()
            if driver_info and driver_info[3] >= num_places and driver_info[4] == 1:
                available_drivers.append({
                    'name': driver_info[0],
                    'latitude': driver_info[1],
                    'longitude': driver_info[2]
                })
                break  # Stop searching if a driver is found

        if available_drivers:
            break  # Stop searching if a driver is found

    if available_drivers:
        return jsonify({'drivers': available_drivers})
    else:
        return jsonify({'error': 'Aucun conducteur disponible pour cette demande.'}), 404


@app.route('/find_another_driver', methods=['POST'])
def find_another_driver():
    data = request.get_json()
    client_lat = data['latitude']
    client_long = data['longitude']
    destination = data.get('destination', 'unknown')
    num_places = data['num_places']

    # Find the next best driver using the same logic as the find_drivers function
    best_clusters = find_best_cluster(client_lat, client_long)
    available_drivers = []

    for cluster_number in best_clusters:
        cluster_drivers = df[df['cluster'] == cluster_number]
        for _, driver in cluster_drivers.iterrows():
            # Fetch driver information from the database including latitude and longitude
            cursor.execute("SELECT d.firstname, dl.latitude, dl.longitude, d.available FROM tbl_driver d JOIN driver_location dl ON d.idd = dl.driver_id WHERE d.idd = %s", (driver['driver_id'],))
            driver_info = cursor.fetchone()
            if driver_info and driver_info[3] >= num_places and driver_info[4] == 1:
                available_drivers.append({
                    'name': driver_info[0],
                    'latitude': driver_info[1],
                    'longitude': driver_info[2]
                })
                break  # Stop searching if a driver is found

        if available_drivers:
            break  # Stop searching if a driver is found

    if available_drivers:
        return jsonify({'driver': available_drivers[0]})
    else:
        return jsonify({'error': 'No more available drivers for this request.'}), 404




if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Exemple : application Flask exécutée sur le port 5000


