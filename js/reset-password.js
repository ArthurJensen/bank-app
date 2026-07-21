 // Read the token from the URL: ?token=abc123
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');

  // If no token in the URL, show the invalid screen immediately
  if (!token) {
    document.getElementById('stepForm').classList.remove('active');
    document.getElementById('stepInvalid').classList.add('active');
  }

  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm');
  const strengthBar = document.getElementById('strengthBar');
  const strengthHint = document.getElementById('strengthHint');
  const submitBtn = document.getElementById('submitBtn');
  const errorBanner = document.getElementById('errorBanner');

  // Live password strength meter
  passwordInput.addEventListener('input', function() {
    document.getElementById('pwField').classList.remove('field-error');
    const v = passwordInput.value;
    let score = 0;
    if (v.length >= 10) score++;
    if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;
    if (/[0-9]/.test(v)) score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;

    const bars = strengthBar.children;
    const colors = ['#C4694B', '#B08D57', '#C9A56E', '#6E9A87'];
    const labels = ['Too short', 'Weak', 'Good', 'Strong'];
    for (let i = 0; i < 4; i++) {
      bars[i].style.background = i < score ? colors[Math.max(score - 1, 0)] : 'var(--ink-line)';
    }
    strengthHint.textContent = v.length
      ? labels[Math.max(score - 1, 0)] || 'Too short'
      : 'Use letters, numbers, and symbols.';
  });

  confirmInput.addEventListener('input', function() {
    document.getElementById('confirmField').classList.remove('field-error');
  });

  document.getElementById('resetForm').addEventListener('submit', function(e) {
    e.preventDefault();
    let valid = true;

    if (passwordInput.value.length < 10) {
      document.getElementById('pwField').classList.add('field-error');
      valid = false;
    }
    if (confirmInput.value !== passwordInput.value || !confirmInput.value) {
      document.getElementById('confirmField').classList.add('field-error');
      valid = false;
    }
    if (!valid) return;

    submitBtn.textContent = 'Updating…';
    submitBtn.disabled = true;
    errorBanner.classList.remove('show');

    fetch('https://bank-app-owi0.onrender.com/api/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: token,
        password: passwordInput.value
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        document.getElementById('stepForm').classList.remove('active');
        document.getElementById('stepSuccess').classList.add('active');
      } else {
        // Token expired between page load and submit
        if (data.message && data.message.includes('expired')) {
          document.getElementById('stepForm').classList.remove('active');
          document.getElementById('stepInvalid').classList.add('active');
        } else {
          errorBanner.textContent = data.message || 'Something went wrong. Please try again.';
          errorBanner.classList.add('show');
          submitBtn.textContent = 'Update password';
          submitBtn.disabled = false;
        }
      }
    })
    .catch(err => {
      errorBanner.textContent = 'Error connecting to server. Please try again.';
      errorBanner.classList.add('show');
      submitBtn.textContent = 'Update password';
      submitBtn.disabled = false;
      console.error(err);
    });
  });