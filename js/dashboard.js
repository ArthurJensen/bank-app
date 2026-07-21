document.addEventListener('DOMContentLoaded', () => {
    const userId = localStorage.getItem('bank_user_id');
    console.log("USER ID FROM LOCAL STORAGE:", userId);

    if (!userId) {
      window.location.href = 'login.html';
      return;
    }

    fetch(`https://bank-app-owi0.onrender.com/api/user/${userId}`)
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          document.getElementById('userGreeting').textContent =
            `Good afternoon, ${data.first_name}.`;
        } else {
          console.error("Could not load user data:", data.message);
        }
      })
      .catch(error => console.error('Error fetching user data:', error));

    fetch(`https://bank-app-owi0.onrender.com/api/user/${userId}/accounts`)
      .then(response => {
        console.log("ACCOUNTS RESPONSE STATUS:", response.status);
        return response.json();
      })
      .then(data => {
        console.log("ACCOUNTS DATA FROM BACKEND:", data);

        const grid = document.getElementById('accountsGrid');

        if (data.status === 'success' && data.accounts.length > 0) {
          grid.innerHTML = '';

          const totalBalance = Number(data.total_accounts_balance);

          document.getElementById('userBalance').textContent =
            totalBalance.toLocaleString('en-US', {
              style: 'currency',
              currency: 'USD'
            });

          data.accounts.forEach(account => {
            const formattedBalance = Number(account.balance).toLocaleString('en-US', {
              style: 'currency',
              currency: 'USD'
            });

            const typeTag =
              account.account_type.charAt(0).toUpperCase() +
              account.account_type.slice(1);

            let subLabel = 'Available now';

            if (account.account_type === 'savings') {
              subLabel = '4.35% APY · earning interest';
            }

            grid.innerHTML += `
              <div class="acct-card">
                <div class="acct-top">
                  <span class="acct-type">${typeTag}</span>
                  <span class="acct-num">••${String(account.id).padStart(4, '0')}</span>
                </div>
                <div class="acct-name">${account.account_name}</div>
                <div class="acct-balance">${formattedBalance}</div>
                <div class="acct-sub">${subLabel}</div>
              </div>
            `;
          });
        } else {
          grid.innerHTML =
            `<p style="color:var(--parchment-dim);font-size:14px;padding:16px 0;">
              No accounts yet. <a href="open-account.html">Open one now →</a>
            </p>`;
        }
      })
      .catch(error => console.error('ACCOUNTS FETCH ERROR:', error));

    const chips = document.querySelectorAll('.filter-chip');
    const rows = document.querySelectorAll('.txn-row');

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        const mode = chip.textContent.trim();

        rows.forEach(function (row) {
          const isCredit = row.querySelector('.txn-amt').classList.contains('credit');

          if (mode === 'All') {
            row.style.display = 'grid';
          } else if (mode === 'Money in') {
            row.style.display = isCredit ? 'grid' : 'none';
          } else if (mode === 'Money out') {
            row.style.display = isCredit ? 'none' : 'grid';
          }
        });
      });
    });

    const logoutBtn = document.getElementById('logoutBtn');

    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('bank_user_id');
        window.location.href = 'login.html';
      });
    }
  });