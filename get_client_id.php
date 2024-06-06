<?php
session_start();

// Check if the client ID is set in the session
if(isset($_SESSION['client_id'])) {
    // Return the client ID as JSON
    echo json_encode(['clientId' => $_SESSION['client_id']]);
} else {
    // Return a default value if the client ID is not set
    echo json_encode(['clientId' => 0]);
}
?>
