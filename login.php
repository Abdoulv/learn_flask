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

                // Store the client ID in the session
                $_SESSION['client_id'] = $row['id']; // Assuming 'id' is the column name for the client ID in tbl_user

                // Update client status to 'pending'
                $client_id = $row['id'];
                $update_sql = "UPDATE `client_request` SET `status` = 'pending' WHERE `client_id` = ?";
                $update_stmt = $conn->prepare($update_sql);
                $update_stmt->bind_param("i", $client_id);
                $update_stmt->execute();

                if ($update_stmt->affected_rows === 0) {
                    // If no rows were affected, it might mean the client does not have a pending request.
                    // You can choose to insert a new row if needed.
                    // For now, we just log the info and proceed.
                    error_log("No pending request updated for client_id: $client_id");
                }

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
