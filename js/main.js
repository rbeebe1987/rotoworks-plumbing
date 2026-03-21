/* ============================================================
   RotoWorks Plumbing — main.js
   Vanilla JS: nav toggle, accordions, scroll, forms, CTA pulse
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ----------------------------------------------------------
     1. Mobile Nav Toggle
     ---------------------------------------------------------- */
  const hamburger = document.querySelector('.hamburger');
  const body = document.body;
  const overlay = document.querySelector('.mobile-drawer-overlay');
  const drawerLinks = document.querySelectorAll('.mobile-drawer a');

  function openDrawer() {
    body.classList.add('mobile-nav-open');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
  }

  function closeDrawer() {
    body.classList.remove('mobile-nav-open');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'false');
    // Also close any open mobile accordions
    document.querySelectorAll('.mobile-dropdown-toggle.open').forEach(function (btn) {
      btn.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      var sub = btn.nextElementSibling;
      if (sub) sub.classList.remove('open');
    });
  }

  if (hamburger) {
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.addEventListener('click', function () {
      if (body.classList.contains('mobile-nav-open')) {
        closeDrawer();
      } else {
        openDrawer();
      }
    });
  }

  // Close drawer when clicking a nav link inside the drawer
  drawerLinks.forEach(function (link) {
    link.addEventListener('click', closeDrawer);
  });

  // Close drawer when clicking the overlay
  if (overlay) {
    overlay.addEventListener('click', closeDrawer);
  }

  // Close drawer on ESC key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && body.classList.contains('mobile-nav-open')) {
      closeDrawer();
    }
  });

  /* ----------------------------------------------------------
     2. Mobile Dropdown Accordions
     ---------------------------------------------------------- */
  var mobileToggles = document.querySelectorAll('.mobile-dropdown-toggle');

  mobileToggles.forEach(function (toggle) {
    toggle.setAttribute('aria-expanded', 'false');
    toggle.addEventListener('click', function () {
      var isOpen = this.classList.contains('open');

      // Close all other accordions first
      mobileToggles.forEach(function (other) {
        other.classList.remove('open');
        other.setAttribute('aria-expanded', 'false');
        var otherSub = other.nextElementSibling;
        if (otherSub) otherSub.classList.remove('open');
      });

      // If this one was closed, open it
      if (!isOpen) {
        this.classList.add('open');
        this.setAttribute('aria-expanded', 'true');
        var submenu = this.nextElementSibling;
        if (submenu) submenu.classList.add('open');
      }
    });
  });

  /* ----------------------------------------------------------
     3. Header Shadow on Scroll
     ---------------------------------------------------------- */
  var header = document.querySelector('.site-header');

  function updateHeaderShadow() {
    if (!header) return;
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', updateHeaderShadow, { passive: true });
  // Run once on load in case page is already scrolled
  updateHeaderShadow();

  /* ----------------------------------------------------------
     4. Smooth Scroll for Anchor Links
     ---------------------------------------------------------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#' || targetId === '') return;

      var target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      // Account for fixed header height
      var headerHeight = header ? header.offsetHeight : 0;
      var targetPos = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

      window.scrollTo({
        top: targetPos,
        behavior: 'smooth'
      });

      // Close mobile drawer if open
      if (body.classList.contains('mobile-nav-open')) {
        closeDrawer();
      }
    });
  });

  /* ----------------------------------------------------------
     5. Form Handling
     ---------------------------------------------------------- */
  var forms = document.querySelectorAll('.request-form form, .contact-form form');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      // Clear previous errors
      form.querySelectorAll('.field-error').forEach(function (el) { el.remove(); });
      form.querySelectorAll('.invalid').forEach(function (el) { el.classList.remove('invalid'); });
      var existingMsg = form.querySelector('.form-error-msg');
      if (existingMsg) existingMsg.remove();

      // Validate required fields
      var valid = true;
      var requiredFields = form.querySelectorAll('[required]');

      requiredFields.forEach(function (field) {
        var value = field.value.trim();

        // Check empty
        if (!value) {
          valid = false;
          showFieldError(field, 'This field is required.');
          return;
        }

        // Check phone pattern if present
        if (field.type === 'tel' && field.pattern) {
          var regex = new RegExp('^' + field.pattern + '$');
          // Also allow common formats: (951) 555-0199, 951-555-0199, etc.
          var digits = value.replace(/\D/g, '');
          if (!regex.test(value) && !regex.test(digits)) {
            valid = false;
            showFieldError(field, 'Please enter a valid 10-digit phone number.');
          }
        }
      });

      if (!valid) return;

      // Submit via fetch
      var submitBtn = form.querySelector('.form-submit');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
      }

      var formData = new FormData(form);

      fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
      })
      .then(function (response) {
        if (response.ok) {
          // Replace form content with success message
          form.innerHTML = '<div class="form-success">' +
            '<i class="fas fa-check-circle" style="font-size:2.5rem;color:#28a745;display:block;margin-bottom:1rem;"></i>' +
            'Thank you! We\'ll call you within 30 minutes.' +
            '</div>';
        } else {
          throw new Error('Server error');
        }
      })
      .catch(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'GET FREE ESTIMATE';
        }
        // Show error message below the form
        var errMsg = document.createElement('p');
        errMsg.className = 'form-error-msg';
        errMsg.textContent = 'Something went wrong. Please call us directly at (951) 555-0199.';
        form.appendChild(errMsg);
      });
    });
  });

  /**
   * Show an inline error message below a form field
   */
  function showFieldError(field, message) {
    field.classList.add('invalid');
    var err = document.createElement('p');
    err.className = 'field-error';
    err.textContent = message;
    field.parentNode.appendChild(err);
  }

  /* ----------------------------------------------------------
     6. Floating CTA Pulse Pause
     ---------------------------------------------------------- */
  var floatingCta = document.querySelector('.floating-cta');
  if (floatingCta) {
    setTimeout(function () {
      floatingCta.classList.add('pulse-stopped');
    }, 5000);
  }

});
