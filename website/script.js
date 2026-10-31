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

const menu = document.querySelector('.menu');
menu.addEventListener('click', () => {
  const links = document.querySelector('.nav-links');
  const open = menu.getAttribute('aria-expanded') === 'true';
  menu.setAttribute('aria-expanded', String(!open));
  links.style.display = open ? '' : 'flex';
  if (!open) Object.assign(links.style, {position:'absolute', top:'68px', left:'14px', right:'14px', padding:'22px', flexDirection:'column', background:'#080d0f', border:'1px solid rgba(155,210,199,.14)'});
});
