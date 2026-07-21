 let selected = null;

  function selectAccount(el) {
    document.querySelectorAll('.account-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    selected = {
      type: el.getAttribute('data-type'),
      label: el.getAttribute('data-label'),
      rate: el.getAttribute('data-rate')
    };
  }

  function setProgress(step) {
    for (let i = 1; i <= 2; i++) {
      const el = document.getElementById('prog' + i);
      const dot = document.getElementById('dot' + i);
      el.classList.remove('active', 'done');
      if (i < step) { el.classList.add('done'); dot.textContent = '✓'; }
      else if (i === step) { el.classList.add('active'); dot.textContent = i; }
      else { dot.textContent = i; }
    }
  }

  function showStep(id) {
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function goTo(n) {
    setProgress(n);
    showStep('step' + n);
  }

  function goToConfirm() {
    if (!selected) {
      // just pick the first one if nothing selected
      const first = document.querySelector('.account-card');
      selectAccount(first);
    }
    document.getElementById('rv-type').textContent = selected.label;
    document.getElementById('rv-rate').textContent = selected.rate;
    setProgress(2);
    showStep('step2');
  }

  function openAccount() {
    const btn = document.getElementById('openBtn');
    btn.textContent = 'Opening your account…';
    btn.disabled = true;

    // Get the logged-in user's ID from localStorage (set by login.html on successful login)
    const userId = localStorage.getItem('bank_user_id');
    if (!userId) {
      alert('You need to be logged in to open an account.');
      window.location.href = 'login.html';
      return;
    }

    fetch('https://bank-app-owi0.onrender.com/api/create-account', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: parseInt(userId),
        account_type: selected.type,
        account_name: selected.label
      })
    })
    .then(res => res.json())
    .then(data => {
      btn.textContent = 'Open my account';
      btn.disabled = false;

      if (data.status === 'success') {
        document.getElementById('newAcctNum').textContent = data.account_number;
        document.getElementById('success-type').textContent = selected.label;
        showStep('stepSuccess');
      } else {
        alert('Could not open account: ' + data.message);
      }
    })
    .catch(err => {
      btn.textContent = 'Open my account';
      btn.disabled = false;
      alert('Error connecting to server. Is the backend running?');
      console.error(err);
    });
  }

  function resetAll() {
    selected = null;
    document.querySelectorAll('.account-card').forEach(c => c.classList.remove('selected'));
    document.getElementById('openBtn').textContent = 'Open my account';
    document.getElementById('openBtn').disabled = false;
    setProgress(1);
    showStep('step1');
  }