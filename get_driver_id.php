<?php
session_start();

header('Content-Type: application/json');

// Check if the client ID is set in the session
if (isset($_SESSION['idd'])) {
    // Return the client ID as JSON
    echo json_encode(['idd' => $_SESSION['idd']]);
} else {
    // Return a default value if the client ID is not set
    echo json_encode(['idd' => 0]);
}
?>
