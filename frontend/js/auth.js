/* ============================================
   POCKET LAWYER 2.0 — Auth Page Logic
   Wired to real Flask JWT backend.
   Zoom-style: Firms created from pricing page.
   Lawyers can register as Private or Join a Firm.
   ============================================ */

let selectedRole = 'client';
let selectedPracticeMode = 'private';

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
  document.querySelectorAll('#role-selector .role-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.role === role);
  });
  document.getElementById('lawyer-fields').style.display = role === 'lawyer' ? 'block' : 'none';
}

function selectPracticeMode(mode) {
  selectedPracticeMode = mode;
  document.querySelectorAll('#practice-selector .role-option').forEach(el => {
    el.classList.toggle('selected', el.dataset.mode === mode);
  });
  document.getElementById('invite-code-field').style.display = mode === 'firm' ? 'block' : 'none';
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
    setTimeout(() => redirectToDashboard(data.user), 800);
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

    // If joining a firm, include invite code
    if (selectedPracticeMode === 'firm') {
      const inviteCode = document.getElementById('reg-invite-code').value.trim();
      if (!inviteCode) {
        Utils.showToast('Please enter your firm invite code', 'error');
        btn.disabled = false;
        btn.textContent = 'Create Account';
        return;
      }
      userData.inviteCode = inviteCode;
    }
  }

  try {
    const data = await API.register(userData);
    const welcomeMsg = data.user.firmName 
      ? `Welcome to ${data.user.firmName}, ${data.user.name}!`
      : `Account created! Welcome, ${data.user.name}!`;
    Utils.showToast(welcomeMsg, 'success');
    setTimeout(() => redirectToDashboard(data.user), 800);
  } catch (err) {
    Utils.showToast(err.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Create Account';
  }
}

function redirectToDashboard(user) {
  // Smart routing based on role and firm membership
  if (user.role === 'firm' || (user.role === 'lawyer' && user.firmRole === 'admin')) {
    window.location.href = 'firm_dashboard.html';
  } else if (user.role === 'lawyer') {
    window.location.href = 'lawyer_dashboard.html';
  } else {
    window.location.href = 'dashboard.html';
  }
}

// Nav toggle
document.getElementById('nav-toggle')?.addEventListener('click', () => {
  document.getElementById('nav-links')?.classList.toggle('open');
});

// If already logged in, redirect
if (API.isLoggedIn()) {
  redirectToDashboard(API.getUser());
}

// Check hash for register tab
if (window.location.hash === '#register') showAuthTab('register');
