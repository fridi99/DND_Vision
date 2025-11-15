  // ---------- Minimal API: Body-Klassen für Hintergrundbilder ----------
  (function(){
    const CLASS_MAP = { blood: 'effect-blood', ice: 'effect-ice', fire: 'effect-fire' };
    let current = null;

    function apply(name){
      clear();
      const cls = CLASS_MAP[name];
      if(!cls) return;
      document.body.classList.add(cls);
      current = name;
      dispatch('applied', { effect: name });
      updateBadge();
    }
    function clear(){
      Object.values(CLASS_MAP).forEach(c => document.body.classList.remove(c));
      if (current !== null) dispatch('cleared', { previous: current });
      current = null;
      updateBadge();
    }
    function get(){ return current; }
    function dispatch(type, detail){ window.dispatchEvent(new CustomEvent(`themefx:${type}`, { detail })); }
    function updateBadge(){
      const el = document.getElementById('currentFx');
      if (el) el.textContent = current ?? 'none';
      markActive(current);
    }
    window.ThemeFX = { apply, clear, get, effects: Object.keys(CLASS_MAP) };
  })();

  // ---------- UI / Modal ----------
  const modal = document.getElementById('fxModal');
  const overlay = document.getElementById('fxOverlay');
  const openBtn = document.getElementById('openFx');
  const closeBtn = document.getElementById('closeFx');
  const saveBtn = document.getElementById('saveFx');
  const clearBtn = document.getElementById('clearFx');
  const grid = document.getElementById('fxGrid');

  let pendingChoice = null;

  function openModal(){
    overlay.classList.add('open');
    modal.classList.add('open');
    pendingChoice = ThemeFX.get();
    markActive(pendingChoice);
  }
  function closeModal(){
    overlay.classList.remove('open');
    modal.classList.remove('open');
  }

  openBtn.addEventListener('click', openModal);
  closeBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', closeModal);

  grid.addEventListener('click', (e)=>{
    const btn = e.target.closest('.fx-btn');
    if(!btn) return;
    pendingChoice = btn.dataset.fx;
    markActive(pendingChoice);
  });

  saveBtn.addEventListener('click', () => {
    if (pendingChoice) ThemeFX.apply(pendingChoice);
    closeModal();
  });

  clearBtn.addEventListener('click', () => {
    ThemeFX.clear();
    pendingChoice = null;
    markActive(null);
  });

  function markActive(name){
    grid.querySelectorAll('.fx-btn').forEach(b=>{
      const active = b.dataset.fx === name;
      b.classList.toggle('active', active);
      b.setAttribute('aria-selected', String(active));
    });
  }

  // ---------- Reveal-on-hover + Toggle + Reset bei Effektwechsel ----------
  (function(){
    const canvas = document.getElementById('revealCanvas');
    const ctx = canvas.getContext('2d');

    // Oberes Bild pro Effekt (gleich wie Body-Backgrounds)
    const EFFECT_TO_IMG = {
      default: 'images/dragon-background.jpeg',
      blood:   'images/blood_effect.jpg',
      ice:     'images/ice_effect.jpg',
      fire:    'images/fire_effect.jpg'
    };

    const toggleBtn = document.getElementById('toggleReveal');
    const topImg = new Image();

    let revealOn = true;   // Toggle-Status
    let topSrc = null;

    toggleBtn.addEventListener('click', () => {
      revealOn = !revealOn;
      toggleBtn.textContent = `Reveal: ${revealOn ? 'ON' : 'OFF'}`;
      // Zustand auf Canvas bleibt bestehen
    });

    function fitCanvas(){
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      if (topImg.complete && topImg.naturalWidth) redrawTop();
    }

    function coverDraw(img){
      const cw = canvas.width, ch = canvas.height;
      const ir = img.width / img.height, cr = cw / ch;
      let w, h, x, y;
      if (cr > ir){ w = cw; h = cw / ir; x = 0; y = (ch - h)/2; }
      else        { h = ch; w = ch * ir; y = 0; x = (cw - w)/2; }
      ctx.drawImage(img, x, y, w, h);
    }

    function redrawTop(){
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0,0,canvas.width,canvas.height);
      coverDraw(topImg);
      ctx.globalCompositeOperation = 'destination-out'; // Brush radiert wieder
    }

    function setTopByEffect(name){
      const src = EFFECT_TO_IMG[name || 'default'];
      if (src === topSrc){ // gleicher Effekt → Maske zurücksetzen
        redrawTop();
        return;
      }
      topSrc = src;
      topImg.onload = redrawTop;
      topImg.src = src;
      if (topImg.complete && topImg.naturalWidth) redrawTop();
    }

    function isOverUi(target){
      return modal.classList.contains('open') ||
             modal.contains(target) ||
             overlay.contains(target) ||
             target.closest?.('.card') ||
             target.closest?.('.modal-panel');
    }

    // weicher Brush
    function eraseAt(x, y){
      if (!revealOn) return; // eingefroren
      const t = document.elementFromPoint(x, y);
      if (isOverUi(t)) return;

      const r = 90;
      const g = ctx.createRadialGradient(x, y, r*0.35, x, y, r);
      g.addColorStop(0, 'rgba(0,0,0,1)');
      g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI*2);
      ctx.fill();
    }

    document.addEventListener('mousemove', e => eraseAt(e.clientX, e.clientY), {passive:true});
    document.addEventListener('touchmove', e => {
      const t = e.touches[0]; if(!t) return;
      eraseAt(t.clientX, t.clientY);
    }, {passive:true});

    window.addEventListener('resize', fitCanvas);

    // Initial
    setTopByEffect(ThemeFX.get());
    fitCanvas();

    // WICHTIG: Bei Effektwechsel Canvas leeren und Top neu deckend zeichnen
    window.addEventListener('themefx:applied', e => {
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0,0,canvas.width,canvas.height);
      setTopByEffect(e.detail.effect);
    });
    window.addEventListener('themefx:cleared', () => {
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0,0,canvas.width,canvas.height);
      setTopByEffect('default');
    });
  })();
