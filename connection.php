<?php

$servername = "localhost"; // Change this to your MySQL server name if it's different
$username = "root"; // Change this to your MySQL username
$password = ""; // Change this to your MySQL password if you have one
$dbname = "login_register_db"; // Change this to your MySQL database name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// // Check connection
// if ($conn->connect_error) {
//     die("Connection failed: " . $conn->connect_error);
// } else {
//     echo "Connection successful!"; // Print this message if the connection is successful
// }

?>
