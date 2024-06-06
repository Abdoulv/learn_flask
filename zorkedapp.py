from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics import silhouette_score
import os

app = Flask(__name__)
CORS(app)

# Database connection function
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='login_register_db'
    )

# Fetch data from the database
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT time_date, latitude, longitude, driver_id FROM driver_location")
data = cursor.fetchall()
df = pd.DataFrame(data, columns=['time_date', 'latitude', 'longitude', 'driver_id'])

# Data preprocessing and clustering
df['time_date'] = pd.to_datetime(df['time_date'], format='%d/%m/%Y-%I:%M:%S %p')
df['hour'] = df['time_date'].dt.hour
df['day_of_week'] = df['time_date'].dt.dayofweek
features = df[['latitude', 'longitude', 'hour', 'day_of_week']].values

# Determine the optimal number of clusters using the silhouette method
silhouette_scores = []
for i in range(2, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    cluster_labels = kmeans.fit_predict(features)
    silhouette_avg = silhouette_score(features, cluster_labels)
    silhouette_scores.append(silhouette_avg)

optimal_clusters_silhouette = np.argmax(silhouette_scores) + 2
kmeans = KMeans(n_clusters=optimal_clusters_silhouette, random_state=42)
kmeans.fit(features)
df['cluster'] = kmeans.predict(features)
cluster_centers = kmeans.cluster_centers_

def find_best_cluster(client_lat, client_long):
    distances = np.sqrt((cluster_centers[:, 0] - client_lat)**2 + (cluster_centers[:, 1] - client_long)**2)
    return distances.argsort()

@app.route('/insert_client_request', methods=['POST'])
def insert_client_request():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Invalid input data")

        print(f"Received request to insert client request data: {data}")
        client_id = data['client_id']
        client_lat = data['latitude']
        client_long = data['longitude']
        num_places = data['num_places']
        destination = data['destination']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert the client request into the database
        cursor.execute("""
            INSERT INTO client_request (client_id, latitude, longitude, destination, num_places)
            VALUES (%s, %s, %s, %s, %s)
        """, (client_id, client_lat, client_long, destination, num_places))
        conn.commit()
        
        return jsonify({'message': 'Client request inserted successfully'})
    except Exception as e:
        print(f"Error inserting client request: {str(e)}")
        return jsonify({'error': f'Error inserting client request: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/find_drivers', methods=['POST'])
def find_drivers():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Invalid input data")

        print(f"Received request with data: {data}")
        client_lat = data['latitude']
        client_long = data['longitude']
        num_places = data['num_places']
        destination = data['destination']
        
        best_clusters = find_best_cluster(client_lat, client_long)
        available_drivers = []

        conn = get_db_connection()
        cursor = conn.cursor()

        for cluster_number in best_clusters:
            cluster_drivers = df[df['cluster'] == cluster_number]
            for _, driver in cluster_drivers.iterrows():
                cursor.execute("SELECT d.firstname, dl.latitude, dl.longitude, d.available FROM tbl_driver d JOIN driver_location dl ON d.idd = dl.driver_id WHERE d.idd = %s", (driver['driver_id'],))
                driver_info = cursor.fetchone()
                if driver_info and len(driver_info) >= 4 and driver_info[3] == 1:  # Assuming driver_info[3] is availability
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
    except Exception as e:
        print(f"Error in find_drivers: {str(e)}")
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update_driver_availability', methods=['POST'])
def update_driver_availability():
    try:
        data = request.get_json()
        driver_id = data['driver_id']
        availability = data['availability']
        
        cursor.execute("UPDATE tbl_driver SET available = %s WHERE idd = %s", (availability, driver_id))
        conn.commit()
        return jsonify({'message': 'Driver availability updated successfully'})
    except Exception as e:
        print(f"Error in update_driver_availability: {str(e)}")
        return jsonify({'error': f'Error updating driver availability: {str(e)}'}), 500

@app.route('/driver_accept', methods=['POST'])
def driver_accept():
    try:
        data = request.get_json()
        driver_id = data['driver_id']
        client_id = data['client_id']
        
        # Logic to handle driver accepting the request
        # Update the database or send notifications as necessary
        return jsonify({'message': 'Driver accepted the client request'})
    except Exception as e:
        print(f"Error in driver_accept: {str(e)}")
        return jsonify({'error': f'Error processing driver acceptance: {str(e)}'}), 500

@app.route('/find_another_driver', methods=['POST'])
def find_another_driver():
    try:
        data = request.get_json()
        client_lat = data['latitude']
        client_long = data['longitude']
        num_places = data['num_places']
        destination = data['destination']
        
        best_clusters = find_best_cluster(client_lat, client_long)
        available_drivers = []

        for cluster_number in best_clusters:
            cluster_drivers = df[df['cluster'] == cluster_number]
            for _, driver in cluster_drivers.iterrows():
                cursor.execute("SELECT d.firstname, dl.latitude, dl.longitude, d.available FROM tbl_driver d JOIN driver_location dl ON d.idd = dl.driver_id WHERE d.idd = %s", (driver['driver_id'],))
                driver_info = cursor.fetchone()
                if driver_info and len(driver_info) >= 4 and driver_info[3] == 1: # Assuming driver_info[3] is availability
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
    except Exception as e:
        print(f"Error in find_another_driver: {str(e)}")
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/get_client_requests', methods=['GET'])
def get_client_requests():
    try:
        # Fetch client requests from the database
        cursor.execute("SELECT client_id, latitude, longitude, destination, num_places FROM client_request WHERE status = 'pending'")
        client_requests = cursor.fetchall()
        
        if client_requests:
            client_request = client_requests[0]  # Get the first pending request
            return jsonify({
                'client_id': client_request[0],
                'latitude': client_request[1],
                'longitude': client_request[2],
                'destination': client_request[3],
                'num_places': client_request[4]
            })
        else:
            return jsonify({'error': 'No client requests found'}), 404
    except Exception as e:
        print(f"Error in get_client_requests: {str(e)}")
        return jsonify({'error': f'Error fetching client requests: {str(e)}'}), 500

if __name__ == '__main__':
    host = os.getenv('IP', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    app.secret_key = os.urandom(24)
    app.run(host=host, port=port)
