 const form = document.getElementById('signupForm');
  const fields = {
    first: document.getElementById('first'),
    last: document.getElementById('last'),
    email: document.getElementById('email'),
    password: document.getElementById('password'),
    confirm: document.getElementById('confirm')
  };
  const ids = { first:'firstField', last:'lastField', email:'emailField', password:'pwField', confirm:'confirmField' };
  const submitBtn = document.getElementById('submitBtn');
  const strengthBar = document.getElementById('strengthBar');
  const strengthHint = document.getElementById('strengthHint');

  function setError(key, on){
    document.getElementById(ids[key]).classList.toggle('field-error', on);
  }

  fields.password.addEventListener('input', function(){
    const v = fields.password.value;
    let score = 0;
    if(v.length >= 10) score++;
    if(/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;
    if(/[0-9]/.test(v)) score++;
    if(/[^A-Za-z0-9]/.test(v)) score++;

    const bars = strengthBar.children;
    const colors = ['var(--danger)', 'var(--brass)', 'var(--brass-bright)', 'var(--forest-bright)'];
    const labels = ['Too short', 'Weak', 'Good', 'Strong'];
    for(let i=0; i<4; i++){
      bars[i].style.background = i < score ? colors[Math.max(score-1,0)] : 'var(--ink-line)';
    }
    strengthHint.textContent = v.length ? labels[Math.max(score-1,0)] || 'Too short' : 'Use at least 10 characters, mixing letters and numbers.';
  });

  Object.keys(fields).forEach(function(key){
    fields[key].addEventListener('input', function(){ setError(key, false); });
  });

  form.addEventListener('submit', function(e){
    e.preventDefault();
    let valid = true;

    if(!fields.first.value.trim()){ setError('first', true); valid = false; }
    if(!fields.last.value.trim()){ setError('last', true); valid = false; }

    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fields.email.value.trim());
    if(!emailOk){ setError('email', true); valid = false; }

    if(fields.password.value.length < 10){ setError('password', true); valid = false; }

    if(fields.confirm.value !== fields.password.value || !fields.confirm.value){
      setError('confirm', true); valid = false;
    }

    if(!document.getElementById('agree').checked){
      valid = false;
      alert('Please agree to the Account Agreement and Privacy Policy to continue.');
    }

    if(valid){
      submitBtn.textContent = 'Creating account…';
      submitBtn.disabled = true;

      // Hit your live Render instance endpoint
      fetch('https://bank-app-owi0.onrender.com/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          first: fields.first.value.trim(),
          last: fields.last.value.trim(),
          email: fields.email.value.trim(),
          password: fields.password.value
        })
      })
      .then(response => response.json())
      .then(data => {
        submitBtn.textContent = 'Create account';
        submitBtn.disabled = false;
        
        if(data.status === 'success') {
            alert(data.message); // Displays "Account created successfully!"
            window.location.href = 'login.html'; // Sends them right over to sign in
        } else {
            alert("Sign up failed: " + data.message);
        }
      })
      .catch(error => {
        submitBtn.textContent = 'Create account';
        submitBtn.disabled = false;
        alert("Error connecting to the registration server.");
        console.error('Error:', error);
      });
    }
  });