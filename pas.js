document.getElementById('resetForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var email = document.getElementById('email').value;
    var message = document.getElementById('message');
    
    // Validate email and show message
    if(email) {
      message.innerHTML = 'Password reset email sent to ' + email;
    } else {
      message.innerHTML = 'Please enter a valid email address';
    }
    
    document.getElementById('resetForm').reset();
  });