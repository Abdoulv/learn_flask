<?php
session_start();
include 'connection.php';

if (isset($_POST['login'])) {

    if (empty($_POST['username']) || empty($_POST['password'])) {
        echo "<script>alert('Please Fill Username and Password');</script>";
        exit;
    }

    $username = $_POST['username'];
    $password = md5($_POST['password']); // Ensure consistency with the registration script

    $sql = "SELECT * FROM `tbl_driver` WHERE `username` = ? AND `password` = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ss", $username, $password);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        // Store driver's information in session, including the idd
        $_SESSION['name'] = $row['name'];
        $_SESSION['username'] = $row['username'];
        $_SESSION['idd'] = $row['idd']; // Assuming idd is the driver's unique identifier in the database
        header('Location: maap.html');
        exit;
    } else {
        echo "<script>alert('Invalid Username or Password');</script>";
        header('Location: indexd.html');
        exit;
    }
}
?>
