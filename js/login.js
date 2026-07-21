 //Gets the information that the user has stored in the html with id "____"
 const form = document.getElementById('loginForm');
  const userField = document.getElementById('userField');
  const pwField = document.getElementById('pwField');
  const username = document.getElementById('username');
  const password = document.getElementById('password');
  const submitBtn = document.getElementById('submitBtn');
 

   //When user clicks on the button with the id of submit let the variable valid = true.
  form.addEventListener('submit', function(e){
    e.preventDefault();
    let valid = true;

    //If username contains only spaces or empty characters state that it is an error, and if there are make valid ≠ true
    if(!username.value.trim()){
      userField.classList.add('field-error');
      valid = false;
    } else {
      userField.classList.remove('field-error');
    }

    //Do the same with the password
    if(!password.value){
      pwField.classList.add('field-error');
      valid = false;
    } else {
      pwField.classList.remove('field-error');
    }

    //Prevents a person from clicking submit multiple times ?
    if(valid){
      submitBtn.textContent = 'Signing in…';
      submitBtn.disabled = true;

      // Send the data to your LIVE Render backend
      fetch('https://bank-app-owi0.onrender.com/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: username.value.trim(), password: password.value })
      })

      // Convert the server response into usable data
      .then(response => response.json())

// Process the response and reset the login button
      .then(data => {
        submitBtn.textContent = 'Log in';
        submitBtn.disabled = false;
        
        // Check the response from Python
        if(data.status === 'success') {
            // Save the user ID to local storage so the dashboard knows who logged in
            localStorage.setItem('bank_user_id', data.user_id);
            // Redirect to the dashboard
            window.location.href = 'dashboard.html';
        } else {
            alert("Login failed: " + data.message);
        }
      })
      
      //If it manages to catch an error while signing in, then state that there is an error.
      .catch(error => {
        submitBtn.textContent = 'Log in';
        submitBtn.disabled = false;
        alert("Error connecting to the server. Is app.py running?");
        console.error('Error:', error);
      });
    }
  });

  // Remove the error highlight when the user starts typing
  [username, password].forEach(function(input){
    input.addEventListener('input', function(){
      input.closest('.field').classList.remove('field-error');
    });
  });