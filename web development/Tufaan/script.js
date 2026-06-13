// ============================================
// pscript.js - Premium AI/ML Portfolio
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // ============================================
  // 1. TYPING ANIMATION
  // ============================================
  const typingElement = document.getElementById('typingText');
  if (typingElement) {
    const roles = ['Aspiring Machine Learning Engineer', 'AI Enthusiast', 'Problem Solver', 'Open Source Contributor'];
    let roleIndex = 0, charIndex = 0, isDeleting = false;
    
    function typeEffect() {
      const fullText = roles[roleIndex];
      if (isDeleting) {
        typingElement.textContent = fullText.substring(0, charIndex - 1);
        charIndex--;
      } else {
        typingElement.textContent = fullText.substring(0, charIndex + 1);
        charIndex++;
      }
      if (!isDeleting && charIndex === fullText.length) {
        isDeleting = true;
        setTimeout(typeEffect, 2000);
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
        setTimeout(typeEffect, 500);
      } else {
        setTimeout(typeEffect, isDeleting ? 50 : 100);
      }
    }
    typeEffect();
  }

  // ============================================
  // 2. NAVBAR SCROLL EFFECT
  // ============================================
  const navbar = document.getElementById('navbar');
  const sections = document.querySelectorAll('section');
  const navLinks = document.querySelectorAll('.nav-link');
  
  function updateNavbar() {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }
  
  function updateActiveSection() {
    let current = '';
    const scrollPos = window.scrollY + 100;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        current = section.getAttribute('id');
      }
    });
    navLinks.forEach(link => {
      link.classList.remove('active');
      const href = link.getAttribute('href');
      if (href === `#${current}`) link.classList.add('active');
    });
  }
  
  window.addEventListener('scroll', () => {
    updateNavbar();
    updateActiveSection();
  });
  updateNavbar();

  // ============================================
  // 3. MOBILE MENU
  // ============================================
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navToggle.classList.toggle('active');
      navMenu.classList.toggle('active');
    });
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navToggle.classList.remove('active');
        navMenu.classList.remove('active');
      });
    });
  }

  // ============================================
  // 4. SMOOTH SCROLLING
  // ============================================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ============================================
  // 5. THEME TOGGLE
  // ============================================
  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      themeToggle.innerHTML = isLight ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      document.body.classList.add('light-theme');
      themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
  }

  // ============================================
  // 6. PROGRESS BARS ANIMATION
  // ============================================
  const progressBars = document.querySelectorAll('.skill-progress');
  const progressObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const width = entry.target.getAttribute('data-width');
        if (width) entry.target.style.width = width;
        progressObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  progressBars.forEach(bar => progressObserver.observe(bar));

  // ============================================
  // 7. SCROLL REVEAL ANIMATIONS
  // ============================================
  const revealElements = [
    ...document.querySelectorAll('.section-header'),
    ...document.querySelectorAll('.about-card'),
    ...document.querySelectorAll('.highlight-item'),
    ...document.querySelectorAll('.skill-category'),
    ...document.querySelectorAll('.timeline-item'),
    ...document.querySelectorAll('.contribution-card'),
    ...document.querySelectorAll('.contact-card'),
    ...document.querySelectorAll('.contact-form-container')
  ];
  
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  
  revealElements.forEach((el, index) => {
    el.classList.add('reveal');
    if (index % 2 === 0) el.classList.add('reveal-left');
    else el.classList.add('reveal-right');
    revealObserver.observe(el);
  });
  
  // Project cards staggered reveal
  const projectCards = document.querySelectorAll('.project-card');
  projectCards.forEach((card, index) => {
    card.classList.add('reveal-scale');
    const cardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add('active'), index * 100);
          cardObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    cardObserver.observe(card);
  });

  // ============================================
  // 8. 3D TILT FOR PROJECT CARDS
  // ============================================
  projectCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -10;
      const rotateY = ((x - centerX) / centerX) * 10;
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });

  // ============================================
  // 9. BACK TO TOP BUTTON
  // ============================================
  const backToTop = document.createElement('button');
  backToTop.className = 'back-to-top';
  backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
  document.body.appendChild(backToTop);
  
  window.addEventListener('scroll', () => {
    if (window.scrollY > 500) backToTop.classList.add('visible');
    else backToTop.classList.remove('visible');
  });
  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // ============================================
  // 10. FLOATING PARTICLES
  // ============================================
  function createParticles() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '0';
    document.body.insertBefore(canvas, document.body.firstChild);
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    
    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    
    function initParticles() {
      particles = [];
      const count = Math.min(60, Math.floor(window.innerWidth / 25));
      for (let i = 0; i < count; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          radius: Math.random() * 2 + 1,
          alpha: Math.random() * 0.3 + 0.1,
          speedX: (Math.random() - 0.5) * 0.3,
          speedY: (Math.random() - 0.5) * 0.3,
          color: Math.random() > 0.6 ? '#8b5cf6' : '#06b6d4'
        });
      }
    }
    
    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
        p.x += p.speedX;
        p.y += p.speedY;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
      });
      requestAnimationFrame(animate);
    }
    
    window.addEventListener('resize', () => {
      resize();
      initParticles();
    });
    resize();
    initParticles();
    animate();
  }
  createParticles();

  // ============================================
  // 11. MOUSE GLOW EFFECT
  // ============================================
  const glow = document.createElement('div');
  glow.style.cssText = `
    position: fixed;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
    transition: transform 0.05s;
  `;
  document.body.appendChild(glow);
  
  document.addEventListener('mousemove', (e) => {
    glow.style.left = e.clientX + 'px';
    glow.style.top = e.clientY + 'px';
  });
  if ('ontouchstart' in window) glow.style.display = 'none';

  // ============================================
  // 12. CONTACT FORM
  // ============================================
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('name')?.value.trim();
      const email = document.getElementById('email')?.value.trim();
      const subject = document.getElementById('subject')?.value.trim();
      const message = document.getElementById('message')?.value.trim();
      
      if (!name || !email || !subject || !message) {
        showMsg('Please fill all fields', 'error');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showMsg('Enter valid email', 'error');
        return;
      }
      
      showMsg('Message sent! I\'ll get back to you soon.', 'success');
      form.reset();
      
      function showMsg(msg, type) {
        const existing = document.querySelector('.form-msg');
        if (existing) existing.remove();
        const div = document.createElement('div');
        div.className = 'form-msg';
        div.textContent = msg;
        div.style.cssText = `
          margin-top: 16px;
          padding: 12px;
          border-radius: 8px;
          text-align: center;
          font-size: 0.9rem;
          background: ${type === 'success' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'};
          color: ${type === 'success' ? '#10b981' : '#ef4444'};
          border: 1px solid ${type === 'success' ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'};
        `;
        form.appendChild(div);
        setTimeout(() => div.remove(), 5000);
      }
    });
  }

  // ============================================
  // 13. TERMINAL WIDGET
  // ============================================
  function createTerminal() {
    const terminalHTML = `
      <div class="terminal-widget" id="terminalWidget">
        <div class="terminal-header">
          <div class="terminal-dot red"></div>
          <div class="terminal-dot yellow"></div>
          <div class="terminal-dot green"></div>
          <div class="terminal-title">monika@portfolio:~/dev</div>
          <button class="terminal-minimize" id="terminalMinimize">−</button>
        </div>
        <div class="terminal-body" id="terminalBody">
          <div class="terminal-line">
            <span class="terminal-prompt">$</span>
            <span class="terminal-command"> echo "Initializing AI/ML Portfolio..."</span>
          </div>
          <div class="terminal-line">
            <span class="terminal-output-success">✓ Initializing...</span>
          </div>
          <div id="terminalCommands"></div>
          <div class="terminal-cursor-line">
            <span class="terminal-prompt">></span>
            <span class="terminal-blink"></span>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', terminalHTML);
    
    const terminal = document.getElementById('terminalWidget');
    const minimizeBtn = document.getElementById('terminalMinimize');
    const commandsContainer = document.getElementById('terminalCommands');
    
    const commands = [
      '> loading projects...',
      '> analyzing codebase...',
      '> training model...',
      '> model accuracy: 94.7%',
      '> deployment successful...',
      '> github contributions synced...',
      '> portfolio optimized...',
      '> ready for internship opportunities'
    ];
    
    setTimeout(() => terminal.classList.add('open'), 1000);
    
    if (minimizeBtn) {
      minimizeBtn.addEventListener('click', () => {
        terminal.classList.toggle('open');
        minimizeBtn.textContent = terminal.classList.contains('open') ? '−' : '+';
      });
    }
    
    commands.forEach((cmd, i) => {
      setTimeout(() => {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerHTML = `<span class="terminal-prompt">></span> ${cmd}`;
        commandsContainer.appendChild(line);
        const body = document.getElementById('terminalBody');
        if (body) body.scrollTop = body.scrollHeight;
      }, 2000 + (i * 500));
    });
    
    setTimeout(() => {
      const success = document.createElement('div');
      success.className = 'terminal-line';
      success.innerHTML = '<span class="terminal-output-success">✓ All systems operational!</span>';
      commandsContainer.appendChild(success);
      const body = document.getElementById('terminalBody');
      if (body) body.scrollTop = body.scrollHeight;
    }, 6000);
  }
  
  createTerminal();

  // ============================================
  // 14. LIGHT THEME STYLES
  // ============================================
  const lightStyles = document.createElement('style');
  lightStyles.textContent = `
    body.light-theme {
      --bg-primary: #f8fafc;
      --bg-secondary: #f1f5f9;
      --bg-tertiary: #e2e8f0;
      --card-bg: rgba(255, 255, 255, 0.7);
      --card-bg-solid: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #334155;
      --text-muted: #64748b;
    }
    body.light-theme .skill-bar { background: rgba(0,0,0,0.1); }
    body.light-theme .terminal-widget { background: #f8fafc; border-color: #8b5cf6; }
    body.light-theme .terminal-body { background: #f8fafc; }
    body.light-theme .terminal-line { color: #334155; }
    body.light-theme .project-card { background: #ffffff; }
  `;
  document.head.appendChild(lightStyles);
  
  console.log('%c✨ Portfolio Ready | Monika Yadav - AI/ML Engineer ✨', 'color: #8b5cf6; font-size: 14px;');
});