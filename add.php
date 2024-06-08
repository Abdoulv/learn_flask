
<?php
include_once('connection.php');

if (isset($_POST['submit'])) {
  $name = $_POST['name'];
  $username = $_POST['username'];
  $pass = md5($_POST['password']); // Consider using a more secure hashing function in the future
  $phone_number = md5($_POST['phone_number']);

  $sql = "INSERT INTO `tbl_user`(`name`, `username`, `password` , `client_number`) VALUES ('$name','$username','$pass','$phone_number')";

  $result = mysqli_query($conn, $sql);


  if($result) {
    echo '<script>
            alert("New client Register Success");
            window.location.href = "login.php";
          </script>';
} else {
    echo '<script>
            alert("Error: ' . mysqli_error($conn) . '");
            window.location.href = "register.html";
          </script>';
}
}


