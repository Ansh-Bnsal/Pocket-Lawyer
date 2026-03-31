/* ============================================
   POCKET LAWYER 2.0 — Auth Page Logic
   Wired to real Flask JWT backend.
   ============================================ */

let selectedRole = 'client';

function showAuthTab(tab) {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');

  if (tab === 'login') {
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
  } else {
    loginForm.style.display = 'none';
    registerForm.style.display = 'block';
    tabLogin.classList.remove('active');
    tabRegister.classList.add('active');
  }
}

function selectRole(role) {
  selectedRole = role;
  document.querySelectorAll('.role-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.role === role);
  });
  document.getElementById('lawyer-fields').style.display = role === 'lawyer' ? 'block' : 'none';
  document.getElementById('firm-fields').style.display = role === 'firm' ? 'block' : 'none';
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const btn = e.target.querySelector('button[type="submit"]');

  btn.disabled = true;
  btn.textContent = 'Signing in...';

  try {
    const data = await API.login(email, password);
    Utils.showToast('Welcome back, ' + data.user.name + '!', 'success');
    setTimeout(() => redirectToDashboard(data.user.role), 800);
  } catch (err) {
    Utils.showToast(err.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Sign In';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Creating account...';

  const userData = {
    name: document.getElementById('reg-name').value,
    email: document.getElementById('reg-email').value,
    password: document.getElementById('reg-password').value,
    role: selectedRole
  };

  if (selectedRole === 'lawyer') {
    userData.specialization = document.getElementById('reg-specialization').value;
    userData.experience = document.getElementById('reg-experience').value;
    userData.barNumber = document.getElementById('reg-bar-number').value;
  } else if (selectedRole === 'firm') {
    userData.firmName = document.getElementById('reg-firm-name').value;
    userData.firmSize = document.getElementById('reg-firm-size').value;
  }

  try {
    const data = await API.register(userData);
    Utils.showToast('Account created! Welcome, ' + data.user.name + '!', 'success');
    setTimeout(() => redirectToDashboard(data.user.role), 800);
  } catch (err) {
    Utils.showToast(err.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Create Account';
  }
}

function redirectToDashboard(role) {
  if (role === 'lawyer') window.location.href = 'lawyer_dashboard.html';
  else if (role === 'firm') window.location.href = 'firm_dashboard.html';
  else window.location.href = 'dashboard.html';
}

// Nav toggle
document.getElementById('nav-toggle')?.addEventListener('click', () => {
  document.getElementById('nav-links')?.classList.toggle('open');
});

// If already logged in, redirect
if (API.isLoggedIn()) {
  redirectToDashboard(API.getUser().role);
}

// Check hash for register tab
if (window.location.hash === '#register') showAuthTab('register');
