
<?php
include_once('connection.php');

if (isset($_POST['submit'])) {
  $name = $_POST['name'];
  $username = $_POST['username'];
  $pass = md5($_POST['password']); // Consider using a more secure hashing function in the future

  $sql = "INSERT INTO `tbl_user`(`name`, `username`, `password`) VALUES ('$name','$username','$pass')";

  $result = mysqli_query($conn, $sql);


  if($result) {
    echo '<script>
            alert("New Driver Register Success");
            window.location.href = "login.php";
          </script>';
} else {
    echo '<script>
            alert("Error: ' . mysqli_error($conn) . '");
            window.location.href = "register.html";
          </script>';
}
}


