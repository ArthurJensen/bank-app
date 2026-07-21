 const fromSelect = document.getElementById('from');
    const availBalance = document.getElementById('availBalance');
    const amountInput = document.getElementById('amount');
    const toInput = document.getElementById('to');
    const form = document.getElementById('sendForm');
    const formView = document.getElementById('formView');
    const confirmView = document.getElementById('confirmView');

    fromSelect.addEventListener('change', function () {
      document.getElementById('fromField').classList.remove('field-error');
      const opt = fromSelect.options[fromSelect.selectedIndex];
      const bal = opt.getAttribute('data-balance');
      availBalance.textContent = bal ? '$' + Number(bal).toLocaleString(undefined, { minimumFractionDigits: 2 }) + ' available' : '\u00A0';
    });

    document.querySelectorAll('.quick-amt').forEach(function (btn) {
      btn.addEventListener('click', function () {
        amountInput.value = btn.getAttribute('data-amt') + '.00';
        document.getElementById('amountField').classList.remove('field-error');
      });
    });

    document.querySelectorAll('.recipient').forEach(function (r) {
      r.addEventListener('click', function () {
        toInput.value = r.getAttribute('data-name');
        document.getElementById('toField').classList.remove('field-error');
      });
    });

    [fromSelect, toInput, amountInput].forEach(function (el) {
      el.addEventListener('input', function () {
        el.closest('.field').classList.remove('field-error');
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      let valid = true;

      if (!fromSelect.value) {
        document.getElementById('fromField').classList.add('field-error');
        valid = false;
      }
      if (!toInput.value.trim()) {
        document.getElementById('toField').classList.add('field-error');
        valid = false;
      }
      const amt = parseFloat(amountInput.value);
      const opt = fromSelect.options[fromSelect.selectedIndex];
      const balance = opt ? parseFloat(opt.getAttribute('data-balance') || 0) : 0;
      if (!amt || amt <= 0 || amt > balance) {
        document.getElementById('amountField').classList.add('field-error');
        valid = false;
      }

      if (!valid) return
      const userId = localStorage.getItem('bank_user_id');

      fetch('https://bank-app-owi0.onrender.com/api/send-money', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sender_id: userId,
          recipient: toInput.value.trim(),
          amount: amt
        })
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            document.getElementById('confirmAmt').textContent = '$' + amt.toLocaleString(undefined, { minimumFractionDigits: 2 });
            document.getElementById('confirmFrom').textContent = opt.textContent;
            document.getElementById('confirmTo').textContent = toInput.value.trim();
            document.getElementById('confirmNote').textContent = document.getElementById('note').value.trim() || '—';

            formView.style.display = 'none';
            confirmView.classList.add('show');
          } else {
            alert('Transfer failed: ' + data.message);
          }
        })
        .catch(error => {
          alert('Error connecting to server.');
          console.error(error);
        });;

      document.getElementById('confirmAmt').textContent = '$' + amt.toLocaleString(undefined, { minimumFractionDigits: 2 });
      document.getElementById('confirmFrom').textContent = opt.textContent;
      document.getElementById('confirmTo').textContent = toInput.value.trim();
      document.getElementById('confirmNote').textContent = document.getElementById('note').value.trim() || '—';

      formView.style.display = 'none';
      confirmView.classList.add('show');
    });

    document.getElementById('sendAnother').addEventListener('click', function () {
      form.reset();
      availBalance.textContent = '\u00A0';
      confirmView.classList.remove('show');
      formView.style.display = 'block';
    });