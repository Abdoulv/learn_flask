
    <?php
    include_once('connection.php');

    if(isset($_POST['submit'])) {
        $firstname = $_POST['firstname'];
        $lastname = $_POST['lastname'];
        $username = $_POST['username'];
        $phone_number = $_POST['phone_number'];
        $pass = md5($_POST['password']);
        $registration_number = $_POST['registration_number'];

        $sql = "INSERT INTO `tbl_driver`(`firstname`, `lastname`, `username`, `phone_number`, `password`, `registration_number`) VALUES ('$firstname', '$lastname', '$username', '$phone_number', '$pass', '$registration_number')";
        $result = mysqli_query($conn, $sql);

        if($result) {
            echo '<script>
                    alert("New Driver Register Success");
                    window.location.href = "loginDriver.php";
                  </script>';
        } else {
            echo '<script>
                    alert("Error: ' . mysqli_error($conn) . '");
                    window.location.href = "registerDriver.html";
                  </script>';
        }
    }
