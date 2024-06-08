from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics import silhouette_score
import os
import numpy as np
from flask_cors import CORS


np.set_printoptions(precision=4, suppress=True)



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

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

def find_best_cluster(client_lat, client_long, client_time):
    client_hour = client_time.hour
    client_day_of_week = client_time.weekday()
    distances = np.sqrt(
        (cluster_centers[:, 0] - client_lat)**2 +
        (cluster_centers[:, 1] - client_long)**2 +
        (cluster_centers[:, 2] - client_hour)**2 +
        (cluster_centers[:, 3] - client_day_of_week)**2
    )
    return distances.argsort()

        
@app.route('/find_drivers', methods=['POST'])
def find_drivers():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid input data'}), 400

        client_id = data['client_id']
        client_lat = data['latitude']
        client_long = data['longitude']
        num_places = data['num_places']
        destination = data['destination']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert client request
        cursor.execute("""
            INSERT INTO client_request (client_id, latitude, longitude, destination, num_places)
            VALUES (%s, %s, %s, %s, %s)
        """, (client_id, client_lat, client_long, destination, num_places))
        conn.commit()
        request_id = cursor.lastrowid

        # Get timestamp of client request
        cursor.execute("SELECT created_at FROM client_request WHERE id = %s", (request_id,))
        client_time = cursor.fetchone()[0]

        # Find best clusters
        best_clusters = find_best_cluster(client_lat, client_long, client_time)
        available_drivers = []

        # Iterate over the best clusters to find the closest driver
        for cluster_number in best_clusters:
            cluster_drivers = df[df['cluster'] == cluster_number]
            for _, driver in cluster_drivers.iterrows():
                cursor.execute("""
                    SELECT d.idd, d.firstname, dl.latitude, dl.longitude, d.phone_number, d.available 
                    FROM tbl_driver d 
                    JOIN driver_location dl ON d.idd = dl.driver_id 
                    WHERE d.idd = %s AND d.available = 1
                """, (driver['driver_id'],))
                driver_info = cursor.fetchone()
                if driver_info:
                    available_drivers.append({
                        'driver_id': driver_info[0],
                        'name': driver_info[1],
                        'latitude': driver_info[2],
                        'longitude': driver_info[3],
                        'phone_number': driver_info[4]
                    })
                    break

            if available_drivers:
                break

        if available_drivers:
            return jsonify({'drivers': available_drivers})
        else:
            return jsonify({'drivers': []})  # Return an empty array if no drivers found
    except Exception as e:
        print(f"Error in find_drivers: {str(e)}")
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/get_client_requests', methods=['GET'])
def get_client_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Fetch pending client requests
        cursor.execute("SELECT * FROM client_request WHERE status = 'pending' ORDER BY created_at DESC LIMIT 1")
        client_request = cursor.fetchone()

        if client_request:
            return jsonify(client_request)
        else:
            return jsonify({'error': 'No pending client requests found'}), 404
    except Exception as e:
        print(f"Error in get_client_requests: {str(e)}")
        return jsonify({'error': f'Error fetching client requests: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/update_driver_availability', methods=['POST'])
def update_driver_availability():
    try:
        data = request.get_json()
        driver_id = data['driver_id']
        availability = data['availability']

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE tbl_driver SET available = %s WHERE idd = %s", (availability, driver_id))
        conn.commit()
        return jsonify({'message': 'Driver availability updated successfully'})
    except Exception as e:
        print(f"Error in update_driver_availability: {str(e)}")
        return jsonify({'error': f'Error updating driver availability: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()
        
@app.route('/driver_accept', methods=['POST'])
def driver_accept():
    cursor = None
    conn = None
    try:
        data = request.get_json()
        driver_id = data['driver_id']
        client_id = data['client_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get driver information
        cursor.execute("SELECT firstname, phone_number FROM tbl_driver WHERE idd = %s", (driver_id,))
        driver_info = cursor.fetchone()
        print(driver_info)
        if driver_info:
            driver_name, driver_phone = driver_info

            # Mark driver as unavailable
            cursor.execute("UPDATE tbl_driver SET available = 0 WHERE idd = %s", (driver_id,))
            
            # Mark client request as accepted
            cursor.execute("UPDATE client_request SET status = 'accepted' WHERE client_id = %s AND status = 'pending'", (client_id,))
            conn.commit()

            print(driver_name)
            print(driver_phone)
            return jsonify({
                'status': 'accepted',
                'driver_name': driver_name,
                'driver_phone': driver_phone
            })
        else:
            return jsonify({'error': 'Driver not found'}), 404
    except Exception as e:
        print(f"Error in driver_accept: {str(e)}")
        return jsonify({'error': f'Error processing driver acceptance: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# @app.route('/find_another_driver', methods=['POST'])
# def find_another_driver():
#     try:
#         data = request.get_json()
#         driver_id = data['driver_id']  # Get driver's ID
#         client_lat = data['latitude']
#         client_long = data['longitude']
#         num_places = data['num_places']
#         destination = data['destination']
        
#         conn = get_db_connection()
#         cursor = conn.cursor()
#           # Get timestamp of client request
#         cursor.execute("SELECT created_at FROM client_request WHERE id = %s", (request_id,))
#         client_time = cursor.fetchone()[0]
        
#         best_clusters = find_best_cluster(client_lat, client_long, client_time)
#         available_drivers = []

#         for cluster_number in best_clusters:
#             cluster_drivers = df[df['cluster'] == cluster_number]
#             for _, driver in cluster_drivers.iterrows():
#                 cursor.execute("""
#                     SELECT d.idd, d.firstname, dl.latitude, dl.longitude, d.phone_number, d.available 
#                     FROM tbl_driver d 
#                     JOIN driver_location dl ON d.idd = dl.driver_id 
#                     WHERE d.idd != %s AND d.available = 1
#                 """, (driver_id,))
#                 driver_info = cursor.fetchone()
#                 if driver_info:
#                     available_drivers.append({
#                         'driver_id': driver_info[0],
#                         'name': driver_info[1],
#                         'latitude': driver_info[2],
#                         'longitude': driver_info[3],
#                         'phone_number': driver_info[4]
#                     })
#                     break
                    

#             if available_drivers:
#                 break

#         if available_drivers:
#             return jsonify({'drivers': available_drivers})
#         else:
#             return jsonify({'error': 'No available drivers found'}), 404
#     except Exception as e:
#         print(f"Error in find_another_driver: {str(e)}")
#         return jsonify({'error': f'Error processing request: {str(e)}'}), 500
#     finally:
#         cursor.close()
#         conn.close()
        
@app.route('/get_driver_location', methods=['POST'])
def get_driver_location():
    try:
        data = request.get_json()
        driver_id = data['driver_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude FROM driver_location WHERE driver_id = %s ORDER BY time_date DESC LIMIT 1", (driver_id,))
        driver_location = cursor.fetchone()

        if driver_location:
            return jsonify({
                'latitude': driver_location[0],
                'longitude': driver_location[1]
            })
        else:
            return jsonify({'error': 'Driver location not found'}), 404
    except Exception as e:
        print(f"Error in get_driver_location: {str(e)}")
        return jsonify({'error': f'Error fetching driver location: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()
        


@app.route('/driver_login', methods=['POST'])
def driver_login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT idd FROM tbl_driver WHERE username = %s AND password = %s", (username, password))
        driver = cursor.fetchone()

        if driver:
            driver_id = driver[0]
            cursor.execute("UPDATE tbl_driver SET available = 1 WHERE idd = %s", (driver_id,))
            conn.commit()
            return jsonify({'driver_id': driver_id})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error in driver_login: {str(e)}")
        return jsonify({'error': f'Error logging in: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
