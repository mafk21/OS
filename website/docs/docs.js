const sections = [...document.querySelectorAll('article > section')];
const toc = document.querySelector('#toc-links');
sections.forEach(section => {
  const title = section.querySelector('h1,h2');
  if (!title) return;
  const link = document.createElement('a');
  link.href = `#${section.id}`;
  link.textContent = title.textContent;
  toc.appendChild(link);
});

const allNavLinks = [...document.querySelectorAll('.docs-sidebar a, #toc-links a')];
const sectionObserver = new IntersectionObserver(entries => {
  const visible = entries.filter(entry => entry.isIntersecting).sort((a,b) => b.intersectionRatio-a.intersectionRatio)[0];
  if (!visible) return;
  allNavLinks.forEach(link => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
}, { rootMargin: '-15% 0px -68% 0px', threshold: [0,.2,.6] });
sections.forEach(section => sectionObserver.observe(section));

document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  const text = button.closest('.code-block').querySelector('code').textContent;
  try { await navigator.clipboard.writeText(text); button.textContent = 'Copied'; }
  catch (_) { button.textContent = 'Select + copy'; }
  setTimeout(() => button.textContent = 'Copy', 1300);
}));

const modal = document.querySelector('#search-modal');
const input = document.querySelector('#doc-search');
const results = document.querySelector('#search-results');
function openSearch(){modal.classList.add('open');modal.setAttribute('aria-hidden','false');setTimeout(()=>input.focus(),20)}
function closeSearch(){modal.classList.remove('open');modal.setAttribute('aria-hidden','true');input.value=''}
document.querySelector('#search-open').addEventListener('click',openSearch);
modal.addEventListener('click',event=>{if(event.target===modal)closeSearch()});
document.addEventListener('keydown',event=>{if(event.key==='/'&&!['INPUT','TEXTAREA'].includes(document.activeElement.tagName)){event.preventDefault();openSearch()}if(event.key==='Escape')closeSearch()});
input.addEventListener('input',()=>{
  const query=input.value.trim().toLowerCase();
  if(!query){results.innerHTML='<p>Type to search every documentation section.</p>';return}
  const matches=sections.filter(section=>section.textContent.toLowerCase().includes(query)).slice(0,8);
  results.innerHTML=matches.length?'':'<p>No matching sections.</p>';
  matches.forEach(section=>{
    const heading=section.querySelector('h1,h2').textContent;
    const body=section.querySelector('p:not(.section-label)')?.textContent||'';
    const link=document.createElement('a');link.className='search-result';link.href=`#${section.id}`;
    link.innerHTML=`<b>${heading}</b><small>${body.slice(0,120)}${body.length>120?'…':''}</small>`;
    link.addEventListener('click',closeSearch);results.appendChild(link);
  });
});

const menu=document.querySelector('.mobile-doc-menu');
const sidebar=document.querySelector('.docs-sidebar');
menu.addEventListener('click',()=>sidebar.classList.toggle('open'));
sidebar.addEventListener('click',event=>{if(event.target.matches('a'))sidebar.classList.remove('open')});
