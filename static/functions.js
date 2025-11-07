// Smooth scroll-driven background color interpolation
// Put this in static/script.js

// Helpers: hex <-> rgb, and linear interpolation
function hexToRgb(hex) {
  const h = hex.replace('#','');
  return {
    r: parseInt(h.substring(0,2), 16),
    g: parseInt(h.substring(2,4), 16),
    b: parseInt(h.substring(4,6), 16)
  };
}


function rgbToHex({r,g,b}) {
  const toHex = n => ('0' + Math.round(n).toString(16)).slice(-2);
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}


function lerp(a, b, t) { 
    return a + (b - a) * t; 
}

function clamp(v, a, b) { 
    return Math.max(a, Math.min(b, v)); 
}

// Get colors from data attributes
const sections = Array.from(document.querySelectorAll('.panel'));
const colors = sections.map(s => s.dataset.color || '#ffffff').map(hexToRgb);

let ticking = false;
let lastScroll = 0;

function update() {
  ticking = false;
  // find center of viewport
  const viewportCenter = window.scrollY + window.innerHeight / 2;

  // find the two sections we're between (current and next)
  let index = sections.findIndex((sec, i) => {
    const rect = sec.getBoundingClientRect();
    const top = window.scrollY + rect.top;
    const bottom = top + rect.height;
    return viewportCenter >= top && viewportCenter < bottom;
  });

  // clamp
  if (index === -1) {
    if (viewportCenter < sections[0].offsetTop) index = 0;
    else index = sections.length - 1;
  }

  const sec = sections[index];
  const rect = sec.getBoundingClientRect();
  const secTop = window.scrollY + rect.top;
  const progress = (viewportCenter - secTop) / rect.height; // 0..1 within section

  const colorA = colors[index];
  const colorB = (index < colors.length - 1) ? colors[index + 1] : colors[index];

  // interpolate each channel
  const r = lerp(colorA.r, colorB.r, clamp(progress, 0, 1));
  const g = lerp(colorA.g, colorB.g, clamp(progress, 0, 1));
  const b = lerp(colorA.b, colorB.b, clamp(progress, 0, 1));

  // set body background
  document.body.style.backgroundColor = rgbToHex({r, g, b});

  // optionally toggle a "dark" class for inner content readability based on luminance
  const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  if (lum < 140) document.body.classList.remove('dark');
  else document.body.classList.add('dark');
}



// use RAF + scroll flag for performance
function onScroll() {
  lastScroll = window.scrollY;
  if (!ticking) {
    window.requestAnimationFrame(update);
    ticking = true;
  }
}

window.addEventListener('scroll', onScroll, { passive: true });
// update once on load
update();
