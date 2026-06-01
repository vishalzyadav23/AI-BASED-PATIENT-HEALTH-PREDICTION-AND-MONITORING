# HealthSync Pro - Quick Reference Card

## 🚀 Copy-Paste Code Snippets

### BUTTONS

```html
<!-- Primary Action -->
<button class="btn btn-primary">Sign In</button>

<!-- Secondary -->
<button class="btn btn-secondary">Cancel</button>

<!-- Danger -->
<button class="btn btn-danger">Delete</button>

<!-- With Icon -->
<button class="btn btn-primary">
  <svg width="16" height="16"><!-- icon --></svg>
  Next
</button>

<!-- Loading -->
<button class="btn btn-primary is-loading">Processing...</button>
```

---

### CARDS

```html
<!-- Basic Card -->
<div class="card">
  <h3>Title</h3>
  <p>Content goes here</p>
</div>

<!-- Card with Header/Footer -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
    <div class="badge badge-stable">Stable</div>
  </div>
  <div class="card-body">Content here</div>
  <div class="card-footer">
    <button class="btn btn-sm btn-primary">Action</button>
  </div>
</div>
```

---

### STATUS BADGES

```html
<!-- Stable -->
<div class="badge badge-stable">✓ Stable</div>

<!-- Alert -->
<div class="badge badge-alert">⚠ Monitor</div>

<!-- Critical -->
<div class="badge badge-critical">🚨 Critical</div>
```

---

### FORMS

```html
<!-- Text Input -->
<div class="form-group">
  <label class="form-label">Email</label>
  <input type="email" class="form-control" placeholder="user@example.com" />
</div>

<!-- Password -->
<div class="form-group">
  <label class="form-label">Password</label>
  <input type="password" class="form-control" />
</div>

<!-- With Error -->
<div class="form-group is-error">
  <label class="form-label">Email</label>
  <input type="email" class="form-control" value="invalid" />
  <span class="form-error">Invalid email</span>
</div>

<!-- With Hint -->
<div class="form-group">
  <label class="form-label">Password</label>
  <input type="password" class="form-control" />
  <span class="form-hint">Min 8 characters</span>
</div>
```

---

### GRIDS

```html
<!-- 1 column (mobile), 2 on tablet, 3 on desktop -->
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-lg">
  <div class="card">Item 1</div>
  <div class="card">Item 2</div>
  <div class="card">Item 3</div>
</div>

<!-- Equal width 2-column -->
<div class="grid grid-cols-2 gap-md">
  <div class="card">Left</div>
  <div class="card">Right</div>
</div>
```

---

### LAYOUTS

```html
<!-- Flexbox - Center Items -->
<div class="flex flex-center gap-md">
  <svg><!-- icon --></svg>
  <span>Centered content</span>
</div>

<!-- Flexbox - Space Between -->
<div class="flex flex-between">
  <h2>Title</h2>
  <button class="btn btn-sm">Action</button>
</div>

<!-- Flexbox - Column -->
<div class="flex flex-col gap-lg">
  <input class="form-control" />
  <input class="form-control" />
  <button class="btn btn-primary btn-full">Submit</button>
</div>
```

---

### ANIMATIONS

```html
<!-- Fade in -->
<div class="animate-in">Content</div>

<!-- Fade in with delay -->
<div class="animate-in animate-delay-1">Item 1</div>
<div class="animate-in animate-delay-2">Item 2</div>
<div class="animate-in animate-delay-3">Item 3</div>

<!-- Slide from left -->
<div class="animate-in-left">Slide left</div>

<!-- Slide from right -->
<div class="animate-in-right">Slide right</div>
```

---

### RESPONSIVE VISIBILITY

```html
<!-- Show on mobile only -->
<div class="mobile-only">Mobile menu</div>

<!-- Show on desktop only -->
<div class="desktop-only">Desktop sidebar</div>

<!-- Hide on mobile -->
<nav class="desktop-only">Navigation</nav>
```

---

### MEDICAL VITALS DISPLAY

```html
<!-- Heart Rate Card -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Heart Rate</h3>
    <div class="badge badge-stable">Normal</div>
  </div>
  <div class="card-body" style="text-align: center;">
    <div
      style="font-size: 2.5rem; font-weight: 700; color: var(--text-primary);"
    >
      72
    </div>
    <div style="color: var(--text-muted); margin-top: 8px;">bpm</div>
  </div>
</div>

<!-- 4-Vitals Grid -->
<div class="grid grid-cols-4 gap-md">
  <!-- HR -->
  <div class="card" style="text-align: center;">
    <div class="card-title" style="font-size: 12px;">❤️ HR</div>
    <div style="font-size: 1.75rem; font-weight: 700;">72</div>
    <div style="color: var(--text-muted); font-size: 12px;">bpm</div>
  </div>

  <!-- SpO2 -->
  <div class="card" style="text-align: center;">
    <div class="card-title" style="font-size: 12px;">🫁 SpO2</div>
    <div style="font-size: 1.75rem; font-weight: 700;">98</div>
    <div style="color: var(--text-muted); font-size: 12px;">%</div>
  </div>

  <!-- Temp -->
  <div class="card" style="text-align: center;">
    <div class="card-title" style="font-size: 12px;">🌡️ Temp</div>
    <div style="font-size: 1.75rem; font-weight: 700;">36.8</div>
    <div style="color: var(--text-muted); font-size: 12px;">°C</div>
  </div>

  <!-- BP -->
  <div class="card" style="text-align: center;">
    <div class="card-title" style="font-size: 12px;">🩸 BP</div>
    <div style="font-size: 1.75rem; font-weight: 700;">120/80</div>
    <div style="color: var(--text-muted); font-size: 12px;">mmHg</div>
  </div>
</div>
```

---

### FULL LOGIN PAGE

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login - HealthSync</title>
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="design-system.css" />
  </head>
  <body>
    <div class="medical-bg"></div>

    <div
      style="min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 16px;"
    >
      <div class="card" style="max-width: 400px; width: 100%;">
        <div style="text-align: center; margin-bottom: 32px;">
          <h2>Welcome Back</h2>
          <p style="color: var(--text-muted); font-size: 14px;">
            Sign in to HealthSync Pro
          </p>
        </div>

        <form style="display: flex; flex-direction: column; gap: 16px;">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              type="email"
              class="form-control"
              placeholder="you@example.com"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              type="password"
              class="form-control"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" class="btn btn-primary btn-full">
            Sign In
          </button>
        </form>

        <div
          style="text-align: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-light);"
        >
          <p style="font-size: 14px; color: var(--text-muted);">
            Don't have an account?
            <a href="#" style="color: var(--primary-500);">Sign up</a>
          </p>
        </div>
      </div>
    </div>
  </body>
</html>
```

---

### ALERT/NOTIFICATION BANNER

```html
<!-- Success -->
<div
  style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); border-left: 4px solid #22c55e; color: #22c55e; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;"
>
  ✓ Operation completed successfully!
</div>

<!-- Warning -->
<div
  style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-left: 4px solid #f59e0b; color: #f59e0b; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;"
>
  ⚠ Please review your input
</div>

<!-- Error -->
<div
  style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-left: 4px solid #ef4444; color: #ef4444; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;"
>
  ✕ Something went wrong. Please try again.
</div>

<!-- Info -->
<div
  style="background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.3); border-left: 4px solid #06b6d4; color: #06b6d4; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;"
>
  ℹ New vitals uploaded successfully
</div>
```

---

### PATIENT CARD (Dashboard)

```html
<div class="card">
  <div class="card-header">
    <div>
      <h3 class="card-title">John Doe</h3>
      <div style="font-size: 12px; color: var(--text-muted);">
        ID: 12345 | Age: 65
      </div>
    </div>
    <div class="badge badge-stable">Stable</div>
  </div>

  <div class="card-body">
    <div class="grid grid-cols-3 gap-md">
      <div style="text-align: center;">
        <div
          style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;"
        >
          HR
        </div>
        <div style="font-size: 1.5rem; font-weight: 700;">72</div>
      </div>
      <div style="text-align: center;">
        <div
          style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;"
        >
          SpO2
        </div>
        <div style="font-size: 1.5rem; font-weight: 700;">98%</div>
      </div>
      <div style="text-align: center;">
        <div
          style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;"
        >
          Temp
        </div>
        <div style="font-size: 1.5rem; font-weight: 700;">36.8°</div>
      </div>
    </div>
  </div>

  <div class="card-footer">
    <button class="btn btn-sm btn-primary" style="flex: 1;">
      View Profile
    </button>
    <button class="btn btn-sm btn-secondary" style="flex: 1;">Monitor</button>
  </div>
</div>
```

---

### STATISTICS BOX

```html
<div class="grid grid-cols-3 gap-lg">
  <!-- Stat 1 -->
  <div class="card">
    <div
      style="color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;"
    >
      Active Patients
    </div>
    <div
      style="font-size: 2.5rem; font-weight: 700; color: var(--primary-500);"
    >
      12
    </div>
    <div style="color: var(--text-muted); font-size: 12px; margin-top: 8px;">
      ↑ 2 new this week
    </div>
  </div>

  <!-- Stat 2 -->
  <div class="card">
    <div
      style="color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;"
    >
      Alerts Today
    </div>
    <div
      style="font-size: 2.5rem; font-weight: 700; color: var(--warning-500);"
    >
      8
    </div>
    <div style="color: var(--text-muted); font-size: 12px; margin-top: 8px;">
      3 resolved
    </div>
  </div>

  <!-- Stat 3 -->
  <div class="card">
    <div
      style="color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;"
    >
      Critical Cases
    </div>
    <div style="font-size: 2.5rem; font-weight: 700; color: var(--danger-500);">
      2
    </div>
    <div style="color: var(--text-muted); font-size: 12px; margin-top: 8px;">
      All monitored
    </div>
  </div>
</div>
```

---

## 🎨 CSS Variables Reference

```css
/* Colors */
--primary-500, --primary-600, --primary-700
--accent-500, --accent-600, --accent-700
--danger-500, --danger-600, --danger-700
--warning-500, --warning-600, --warning-700
--text-primary, --text-secondary, --text-muted
--bg-dark, --bg-darker, --bg-card

/* Spacing */
--sp-xs, --sp-sm, --sp-md, --sp-lg, --sp-xl, --sp-2xl, --sp-3xl

/* Radius */
--radius-sm, --radius-md, --radius-lg, --radius-xl, --radius-2xl

/* Effects */
--shadow-sm, --shadow-md, --shadow-lg, --shadow-xl, --shadow-glow

/* Transitions */
--transition-fast, --transition-base, --transition-slow
```

---

## 📱 Responsive Helpers

```html
<!-- Stack vertically on mobile -->
<div class="grid grid-cols-1 md:grid-cols-2">
  <!-- Full width on mobile, 50% on desktop -->
  <div style="width: 100%; width: 50%; /* fallback */">
    <!-- Hide on mobile -->
    <nav class="desktop-only">
      <!-- Show on mobile only -->
      <button class="mobile-only">Menu</button>
    </nav>
  </div>
</div>
```

---

## 🎯 Common Patterns

**Dark mode by default** - No additional setup needed!

**Professional consistency** - All components follow the same spacing, colors, typography.

**Responsive first** - Mobile-optimized, scales beautifully to desktop.

**Accessibility included** - Focus states, ARIA labels, semantic HTML built-in.

---

**Save this file for quick reference!**
