/* =========================================================
   Sumit Kanchole — Portfolio interactions
   No dependencies. Every enhancement degrades gracefully.
   ========================================================= */
(() => {
  "use strict";

  const $ = (s, ctx = document) => ctx.querySelector(s);
  const $$ = (s, ctx = document) => [...ctx.querySelectorAll(s)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Hero: entrance + pointer parallax ---------- */
  const hero = $("[data-hero]");
  const heroTitle = $(".hero-title");
  if (heroTitle) {
    $$(".reveal-up", heroTitle).forEach((el, i) => (el.style.transitionDelay = `${0.2 + i * 0.12}s`));
  }
  requestAnimationFrame(() => requestAnimationFrame(() => {
    heroTitle?.classList.add("is-loaded");
    hero?.classList.add("is-ready");
  }));

  if (hero && !reduceMotion && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    let raf = 0;
    hero.addEventListener("pointermove", (e) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        const r = hero.getBoundingClientRect();
        hero.style.setProperty("--mx", (((e.clientX - r.left) / r.width) * 2 - 1).toFixed(3));
        hero.style.setProperty("--my", (((e.clientY - r.top) / r.height) * 2 - 1).toFixed(3));
        raf = 0;
      });
    });
    hero.addEventListener("pointerleave", () => {
      hero.style.setProperty("--mx", 0);
      hero.style.setProperty("--my", 0);
    });
  }

  /* ---------- Arch scene: AI answer → annotator flags → fix → score (loops) ---------- */
  const evalCard = $("[data-eval]");
  const gauge = $("[data-gauge]");
  if (evalCard && gauge) {
    const words = $$(".ec-text .w", evalCard);
    const bad = $("[data-bad]", evalCard);
    const cursor = $("[data-cursor]", evalCard);
    const num = $("[data-gauge-num]");
    const score = Number(gauge.dataset.score) || 0;
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const setGauge = (v) => {
      gauge.style.setProperty("--t", score ? (v / score).toFixed(3) : 1);
      num.textContent = Math.round(v);
    };
    const moveCursor = (x, y) => {
      cursor.style.setProperty("--cx", `${x}px`);
      cursor.style.setProperty("--cy", `${y}px`);
    };
    const park = () => moveCursor(evalCard.clientWidth - 46, evalCard.clientHeight - 18);
    const fillGauge = (to, dur) =>
      new Promise((done) => {
        const t0 = performance.now();
        const step = (now) => {
          const t = Math.min((now - t0) / dur, 1);
          setGauge(to * (1 - Math.pow(1 - t, 3)));
          t < 1 ? requestAnimationFrame(step) : done();
        };
        requestAnimationFrame(step);
      });

    if (reduceMotion) {
      words.forEach((w) => w.classList.add("on")); // static, final state
      cursor.style.display = "none";
    } else {
      let visible = true;
      new IntersectionObserver(([e]) => (visible = e.isIntersecting)).observe(evalCard);

      (async () => {
        park();
        await sleep(900); // let the hero entrance play first
        for (;;) {
          if (!visible || document.hidden) { await sleep(600); continue; }

          evalCard.classList.remove("s-flag", "s-fix", "s-done");
          gauge.classList.remove("is-full");
          words.forEach((w) => w.classList.remove("on"));
          setGauge(0);
          park();
          await sleep(600);

          for (const w of words) { // the AI "types" its answer
            w.classList.add("on");
            await sleep(w === bad ? 260 : 140);
          }
          await sleep(450);

          // annotator moves to the wrong fact and flags it
          moveCursor(bad.offsetLeft + bad.offsetWidth / 2 - 3, bad.offsetTop + bad.offsetHeight - 6);
          await sleep(950);
          cursor.classList.add("click");
          evalCard.classList.add("s-flag");
          await sleep(300);
          cursor.classList.remove("click");
          await sleep(400);
          evalCard.classList.add("s-fix"); // correction appears
          await sleep(650);

          park();
          evalCard.classList.add("s-done"); // review chips pop in
          await fillGauge(score, 1300);
          gauge.classList.add("is-full");
          await sleep(3400);
        }
      })();
    }
  }

  /* ---------- Header: glass state on scroll ---------- */
  const header = $("#header");
  const toTop = $("#to-top");
  let scrollTicking = false;
  const onScroll = () => {
    const y = window.scrollY;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    header?.classList.toggle("is-scrolled", y > 12);
    header?.style.setProperty("--progress", max > 0 ? (y / max).toFixed(4) : 0);
    toTop?.classList.toggle("is-shown", y > 700);
    scrollTicking = false;
  };
  window.addEventListener("scroll", () => {
    if (!scrollTicking) { scrollTicking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  const menuBtn = $("#menu-btn");
  const navLinks = $("#nav-links");
  const setMenu = (open) => {
    if (!navLinks || !menuBtn) return;
    navLinks.classList.toggle("is-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  };
  menuBtn?.addEventListener("click", () => setMenu(!navLinks.classList.contains("is-open")));
  $$("#nav-links a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => e.key === "Escape" && setMenu(false));
  document.addEventListener("click", (e) => {
    if (navLinks?.classList.contains("is-open") && !navLinks.contains(e.target) && !menuBtn.contains(e.target)) setMenu(false);
  });

  /* ---------- Active nav link ---------- */
  const navTargets = $$(".nav-link[data-section]")
    .map((l) => document.getElementById(l.dataset.section))
    .filter(Boolean);
  if (navTargets.length) {
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        $$(".nav-link").forEach((l) => l.classList.toggle("is-active", l.dataset.section === entry.target.id));
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    navTargets.forEach((t) => spy.observe(t));
  }

  /* ---------- Scroll reveal (staggered within groups) ---------- */
  $$(".about-grid, .svc-grid, .xp-grid, .skill-grid").forEach((group) =>
    $$(".reveal", group).forEach((el, i) => (el.style.transitionDelay = `${Math.min(i * 0.08, 0.4)}s`))
  );
  const revealer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      obs.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  $$(".reveal").forEach((el) => revealer.observe(el));

  /* ---------- Count-up numbers ---------- */
  const countUp = (el) => {
    const target = Number(el.dataset.count) || 0;
    const suffix = el.dataset.suffix || "";
    if (reduceMotion) { el.textContent = target + suffix; return; }
    const start = performance.now();
    const duration = 1400;
    const step = (now) => {
      const t = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - t, 4))) + suffix;
      if (t < 1) requestAnimationFrame(step);
    };
    el.textContent = "0" + suffix;
    requestAnimationFrame(step);
  };
  const counter = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      countUp(entry.target);
      obs.unobserve(entry.target);
    });
  }, { threshold: 0.6 });
  $$("[data-count]").forEach((el) => counter.observe(el));

  /* ---------- Toast ---------- */
  const toast = $("#toast");
  let toastTimer;
  const showToast = (msg) => {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("is-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-show"), 2600);
  };

  /* ---------- Copy email ---------- */
  $$("[data-copy]").forEach((btn) =>
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        showToast("Email copied to clipboard ✓");
      } catch {
        showToast(btn.dataset.copy);
      }
    })
  );

  /* ---------- Contact form → Flask API (mailto fallback) ---------- */
  const form = $("#contact-form");
  if (form) {
    const note = $("#form-note");
    const submit = $("#contact-submit");
    const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const RULES = {
      name: (v) => (v.length < 2 ? "Please enter at least 2 characters." : ""),
      email: (v) => (!EMAIL_RE.test(v) ? "Please enter a valid email address." : ""),
      message: (v) => (v.length < 10 ? "Please enter at least 10 characters." : ""),
    };

    const setFieldError = (name, msg) => {
      const input = form.elements[name];
      const field = input?.closest(".field");
      if (!field) return;
      field.classList.toggle("has-error", !!msg);
      input.setAttribute("aria-invalid", msg ? "true" : "false");
      const slot = $(".field-error", field);
      if (slot) slot.textContent = msg || "";
    };
    const setNote = (msg, isError = false) => {
      note.textContent = msg;
      note.classList.toggle("is-error", isError);
    };
    const mailtoFallback = ({ name, email, message }) => {
      const subject = encodeURIComponent(`Portfolio enquiry from ${name}`);
      const body = encodeURIComponent(`${message}\n\n— ${name}\n${email}`);
      window.location.href = `mailto:${form.dataset.email}?subject=${subject}&body=${body}`;
    };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = Object.fromEntries([...new FormData(form)].map(([k, v]) => [k, String(v).trim()]));

      let firstInvalid = null;
      Object.entries(RULES).forEach(([name, rule]) => {
        const msg = rule(data[name] || "");
        setFieldError(name, msg);
        if (msg && !firstInvalid) firstInvalid = form.elements[name];
      });
      if (firstInvalid) {
        setNote("Please fix the highlighted fields.", true);
        firstInvalid.focus();
        return;
      }

      const endpoint = form.dataset.endpoint;
      if (!endpoint) { // static export: no backend available
        mailtoFallback(data);
        setNote("Opening your email client…");
        return;
      }

      submit.disabled = true;
      submit.classList.add("is-loading");
      setNote("Sending…");
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(data),
        });
        const body = await res.json().catch(() => ({}));
        if (res.ok) {
          form.reset();
          setNote("Message sent. I'll get back to you soon.");
          showToast("Thanks! Your message is on its way ✓");
        } else if (res.status === 400 && body.fields) {
          Object.entries(body.fields).forEach(([k, msg]) => setFieldError(k, msg));
          setNote(body.error || "Please fix the highlighted fields.", true);
        } else if (res.status === 429) {
          setNote(body.error || "Too many messages. Please try again later.", true);
        } else {
          throw new Error(body.error || `HTTP ${res.status}`);
        }
      } catch {
        setNote("Couldn't reach the server, so I've opened your email app instead.", true);
        mailtoFallback(data);
      } finally {
        submit.disabled = false;
        submit.classList.remove("is-loading");
      }
    });
    $$(".field input, .field textarea", form).forEach((f) => f.addEventListener("input", () => setFieldError(f.name, "")));
  }

  /* ---------- Local time ---------- */
  const timeEl = $("#local-time");
  if (timeEl) {
    const fmt = new Intl.DateTimeFormat("en-IN", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: timeEl.dataset.tz || "Asia/Kolkata" });
    const tick = () => (timeEl.textContent = fmt.format(new Date()));
    tick();
    setInterval(tick, 30_000);
  }
})();
