// The team's documents as pages of the site: page images rendered by prototype/build_doc_pages.py, PT or EN.
const $ = (s) => document.querySelector(s);
const params = new URLSearchParams(location.search);
const doc = params.get('d') || 'report';
let lang = params.get('lang') || (() => { try { return localStorage.getItem('tt-doc-lang'); } catch { return null; } })() || 'pt';

const manifest = await fetch('/web/docs/manifest.json').then((r) => r.json()).catch(() => null);

function render() {
  document.querySelectorAll('.docs a').forEach((a) => a.toggleAttribute('aria-current', a.dataset.doc === doc) || a.removeAttribute('aria-current'));
  document.querySelectorAll('.docs a').forEach((a) => { if (a.dataset.doc === doc) a.setAttribute('aria-current', 'page'); });
  document.querySelectorAll('.lang button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === lang)));
  const d = manifest?.[doc], e = d?.[lang];
  if (!e) {
    $('#doctitle').textContent = 'Document not built yet';
    $('#docmeta').textContent = 'Run: python3 prototype/build_doc_pages.py';
    $('#sheets').replaceChildren(); $('#dl').hidden = true; return;
  }
  document.title = `ThingTracker · ${d.title[lang]}`;
  $('#doctitle').textContent = d.title[lang];
  $('#docmeta').textContent = `${e.pages.length} ${lang === 'pt' ? (e.pages.length === 1 ? 'página' : 'páginas') : (e.pages.length === 1 ? 'page' : 'pages')} · PDF`;
  $('#dl').hidden = false; $('#dl').href = `/web/docs/${e.pdf}`; $('#dl').setAttribute('download', `ThingTracker - ${d.title[lang]}.pdf`);
  const lead = e.lead ? `<figure class="sheet wide"><img src="/web/docs/${e.lead}" alt="${d.title[lang]}: diagram"></figure>` : '';
  $('#sheets').innerHTML = lead + e.pages.map((p, i) =>
    `<figure class="sheet"><img src="/web/docs/${p}" alt="${d.title[lang]}, ${lang === 'pt' ? 'página' : 'page'} ${i + 1}" loading="${i < 2 ? 'eager' : 'lazy'}"><figcaption>${i + 1}</figcaption></figure>`).join('');
}

document.querySelector('.lang').addEventListener('click', (ev) => {
  const b = ev.target.closest('button[data-lang]'); if (!b) return;
  lang = b.dataset.lang;
  try { localStorage.setItem('tt-doc-lang', lang); } catch { /* private window */ }
  const u = new URL(location.href); u.searchParams.set('lang', lang); history.replaceState(null, '', u);
  render();
});
render();
