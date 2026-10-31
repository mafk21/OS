// Original, dependency-free interaction layer inspired by modern motion libraries.
// Every effect respects reduced motion and the site makes no network requests.
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const headline = document.querySelector('.hero-copy h1');
if (headline && !reduceMotion) {
  let wordIndex = 0;
  [...headline.childNodes].forEach(node => {
    if (node.nodeType !== Node.TEXT_NODE || !node.textContent.trim()) return;
    const fragment = document.createDocumentFragment();
    node.textContent.split(/(\s+)/).forEach(part => {
      if (!part.trim()) { fragment.append(part); return; }
      const word = document.createElement('span');
      word.className = 'word'; word.textContent = part;
      word.style.animationDelay = `${wordIndex++ * 85}ms`;
      fragment.append(word);
    });
    node.replaceWith(fragment);
  });
  const emphasis = headline.querySelector('em');
  if (emphasis) {
    const text = emphasis.textContent; emphasis.textContent = '';
    const word = document.createElement('span'); word.className = 'word'; word.textContent = text;
    word.style.animationDelay = `${wordIndex * 85}ms`; emphasis.append(word);
  }
}

const progress = document.querySelector('.scroll-progress');
const updateProgress = () => {
  const range = document.documentElement.scrollHeight - innerHeight;
  progress.style.transform = `scaleX(${range > 0 ? scrollY / range : 0})`;
};
addEventListener('scroll', updateProgress, { passive: true }); updateProgress();

const editions = document.querySelectorAll('[data-edition]');
editions.forEach(button => button.addEventListener('click', () => {
  editions.forEach(item => item.classList.toggle('active', item === button));
  document.querySelectorAll('.humanoid').forEach(image => {
    image.classList.toggle('active', image.id === `${button.dataset.edition}-image`);
  });
}));

const commands = {
  universal: 'git clone https://github.com/mafk21/OS.git && cd OS\npython3 install_jarvis.py --install --launch',
  windows: 'git clone https://github.com/mafk21/OS.git && cd OS\npy install_jarvis.py --install --launch',
  macos: 'git clone https://github.com/mafk21/OS.git && cd OS\npython3 install_jarvis.py --install --launch',
  linux: 'git clone https://github.com/mafk21/OS.git && cd OS\npython3 install_jarvis.py --install --launch'
};
const code = document.querySelector('#install-code');
document.querySelectorAll('[data-os]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-os]').forEach(item => item.classList.toggle('active', item === button));
  code.innerHTML = commands[button.dataset.os].replace('\n', '<br>');
}));

document.querySelector('#copy-command').addEventListener('click', async event => {
  const selected = document.querySelector('[data-os].active').dataset.os;
  try {
    await navigator.clipboard.writeText(commands[selected]);
    event.currentTarget.textContent = 'COPIED';
    setTimeout(() => event.currentTarget.textContent = 'COPY', 1400);
  } catch (_) {
    event.currentTarget.textContent = 'SELECT + COPY';
  }
});

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(element => observer.observe(element));

document.querySelectorAll('.spotlight-card').forEach(card => {
  const light = document.createElement('i'); light.className = 'card-light'; card.prepend(light);
  card.addEventListener('pointermove', event => {
    const box = card.getBoundingClientRect();
    light.style.left = `${event.clientX - box.left}px`;
    light.style.top = `${event.clientY - box.top}px`;
  });
});

const countObserver = new IntersectionObserver(entries => entries.forEach(entry => {
  if (!entry.isIntersecting) return;
  const item = entry.target; const target = Number(item.dataset.count);
  if (reduceMotion) { item.textContent = target.toLocaleString() + (item.dataset.suffix || ''); return; }
  item.classList.add('counting'); const started = performance.now(); const duration = 1100;
  const tick = now => {
    const t = Math.min(1, (now - started) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    item.textContent = Math.round(target * eased).toLocaleString() + (item.dataset.suffix || '');
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick); countObserver.unobserve(item);
}), { threshold: .6 });
document.querySelectorAll('[data-count]').forEach(item => countObserver.observe(item));

if (!reduceMotion) document.querySelectorAll('.button').forEach(button => {
  button.classList.add('magnetic');
  button.addEventListener('pointermove', event => {
    const box = button.getBoundingClientRect();
    button.style.transform = `translate(${(event.clientX-box.left-box.width/2)*.1}px,${(event.clientY-box.top-box.height/2)*.16}px)`;
  });
  button.addEventListener('pointerleave', () => button.style.transform = '');
});

const field = document.querySelector('#signal-field');
if (field && !reduceMotion) {
  const context = field.getContext('2d'); let points = []; let frame;
  const resizeField = () => {
    const ratio = Math.min(devicePixelRatio || 1, 1.5); field.width = innerWidth * ratio; field.height = 900 * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    points = Array.from({length: Math.min(54, Math.floor(innerWidth/24))}, () => ({x:Math.random()*innerWidth,y:Math.random()*780,vx:(Math.random()-.5)*.14,vy:(Math.random()-.5)*.14}));
  };
  const drawField = () => {
    context.clearRect(0,0,innerWidth,900);
    points.forEach((point,index) => {
      point.x += point.vx; point.y += point.vy;
      if(point.x<0||point.x>innerWidth)point.vx*=-1;if(point.y<0||point.y>800)point.vy*=-1;
      context.fillStyle='rgba(124,249,232,.38)';context.fillRect(point.x,point.y,1,1);
      for(let i=index+1;i<points.length;i++){const other=points[i],dx=point.x-other.x,dy=point.y-other.y,d=Math.hypot(dx,dy);if(d<125){context.strokeStyle=`rgba(124,249,232,${.07*(1-d/125)})`;context.beginPath();context.moveTo(point.x,point.y);context.lineTo(other.x,other.y);context.stroke()}}
    }); frame=requestAnimationFrame(drawField);
  };
  resizeField(); drawField(); addEventListener('resize', resizeField, {passive:true});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelAnimationFrame(frame);else drawField()});
}

const menu = document.querySelector('.menu');
menu.addEventListener('click', () => {
  const links = document.querySelector('.nav-links');
  const open = menu.getAttribute('aria-expanded') === 'true';
  menu.setAttribute('aria-expanded', String(!open));
  links.style.display = open ? '' : 'flex';
  if (!open) Object.assign(links.style, {position:'absolute', top:'68px', left:'14px', right:'14px', padding:'22px', flexDirection:'column', background:'#080d0f', border:'1px solid rgba(155,210,199,.14)'});
});
