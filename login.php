<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);
ini_set('log_errors', 1);
ini_set('error_log', 'path/to/error.log'); // Replace with the desired path for the error log file
session_start();
include 'connection.php';

if (isset($_POST['login'])) {
    // Check if username and password fields are not empty
    if (empty($_POST['username']) || empty($_POST['password'])) {
        $error = "Please Fill Username and Password";
    } else {
        $username = $_POST['username'];
        $password = md5($_POST['password']); // Consider using a more secure hashing function in the future

        // Sanitize username to prevent potential SQL injection (optional)
        $username = htmlspecialchars($username);

        $sql = "SELECT * FROM `tbl_user` WHERE `username` = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            if ($password === $row['password']) {
                // Successful login
                session_regenerate_id();
                $_SESSION['name'] = $row['name'];
                $_SESSION['username'] = $row['username'];
                header('Location: map.html');
                exit;
            } else {
                // Invalid password
                $error = "Invalid Password";
            }
        } else {
            // Invalid username
            $error = "Invalid Username";
        }
    }

    if (isset($error)) {
        echo "<script>alert('" . $error . "');</script>";
        header('Location: indexc.html');
        exit;
    }
}
?>