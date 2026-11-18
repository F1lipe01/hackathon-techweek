// The product video, scripted: the real app copy (app.js) runs on simulated data, and a timeline taps through
// the ThingTracker flow with a visible finger. Recorded by prototype/record_demo.mjs at 1920 x 1080.
// Nothing here talks to the real home or the camera: every /api call is answered below.
(() => {
  const today = (h, m) => { const d = new Date(); d.setHours(h, m, 0, 0); return d.getTime() / 1000; };
  const home = {
    name: 'Hack 3', source: 'demo',
    rooms: [{ id: 'work-room', name: 'Work Room' }],
    devices: [
      { id: 'cam', name: 'Camera', type: 'camera', room_id: 'work-room', status: 'On', raised: 0 },
      { id: 'contact', name: 'Contact sensor', type: 'contactSensor', room_id: null, status: 'Open', raised: 1 },
      { id: 'light', name: 'Light', type: 'bulb', room_id: null, status: 'Disconnected', raised: 0 },
      { id: 'plug', name: 'Plug', type: 'plug', room_id: null, status: '0,0 W', raised: 1 },
      { id: 'hub', name: 'Security hub', type: 'gateway', room_id: null, status: 'On', raised: 0 },
      { id: 'smoke', name: 'Smoke sensor', type: 'smokeSensor', room_id: null, status: 'On', raised: 0 },
      { id: 'temp', name: 'Temperature sensor', type: 'temperatureSensor', room_id: null, status: '23.5 °C | 65.7 %', raised: 0 },
    ],
  };
  const D = { things: [], rules: [], events: [], enrol: null, boxes: [] };
  window.DEMO = D;
  window.DEMO_CAM = '/crops/demo-cam-1.jpg';
  let ev = 0;
  const addEvent = (kind, text, extra = {}) => D.events.unshift({ id: 'e' + (++ev), ts: Date.now() / 1000, kind, text, ...extra });
  const state = () => ({
    things: D.things.map((t) => ({ ...t })), rules: D.rules, events: D.events, enrol: D.enrol, zones: [], home,
    edge: { online: true, state: D.enrol ? 'registering' : 'idle', checked: 0, analysed: 0 },
    settings: { ai: false, budget_usd: 3 }, spend: { usd: 0, calls: 0 },
  });
  const json = (o) => new Response(JSON.stringify(o), { status: 200, headers: { 'Content-Type': 'application/json' } });
  const pause = (ms) => new Promise((r) => setTimeout(r, ms));

  window.fetch = async (input, opts = {}) => {
    const u = typeof input === 'string' ? input : input.url, method = (opts.method || 'GET').toUpperCase();
    if (u.startsWith('/api/state')) return json(state());
    if (u.startsWith('/api/devices')) return json(home);
    if (u.startsWith('/api/edge/boxes')) return json({ boxes: D.boxes, age: D.boxes.length ? 0 : 99, online: true, state: 'idle' });
    if (u === '/api/things' && method === 'POST') {
      const b = JSON.parse(opts.body), id = b.name.toLowerCase().replace(/[^a-z]/g, '');
      if (!D.things.find((t) => t.id === id)) D.things.push({ id, name: b.name, description: b.description, created: Date.now() / 1000, fingerprint: null, last_seen: null });
      return json({ id });
    }
    if (/\/api\/things\/[^/]+\/enrol/.test(u)) {
      const id = decodeURIComponent(u.split('/')[3]);
      D.enrol = { thing_id: id, name: D.things.find((t) => t.id === id)?.name, got: 0, target: 8 };
      return json(D.enrol);
    }
    if (/\/api\/things\/[^/]+\/sightings/.test(u)) return json({ sightings: [] });
    if (u === '/api/assistant') {
      const text = JSON.parse(opts.body).text.toLowerCase();
      await pause(1100);
      const wallet = D.things.find((t) => t.id === 'wallet');
      if (text.includes('tell me')) {
        const r = { id: 'r-1', title: 'Left home without the wallet', sentence: text, active: true };
        D.rules.unshift(r);
        return json({ kind: 'sensor', sensor: r });
      }
      return json({ kind: 'answer', answer: 'On the hall table, in the Work Room, at 15:02.', thing: wallet, candidates: [] });
    }
    return json({ ok: true });
  };

  // the camera inside the app shows the scripted frames, never a real stream
  const camSrc = (img) => { if (img.getAttribute('src')?.includes('/api/kit/stream')) img.setAttribute('src', window.DEMO_CAM); };
  new MutationObserver((ms) => ms.forEach((m) => {
    if (m.type === 'attributes' && m.target.tagName === 'IMG') camSrc(m.target);
    m.addedNodes?.forEach((n) => { if (n.nodeType === 1) { if (n.tagName === 'IMG') camSrc(n); n.querySelectorAll?.('img').forEach(camSrc); } });
  })).observe(document, { subtree: true, childList: true, attributes: true, attributeFilter: ['src'] });

  // ---------------------------------------------------------------- the story
  const $ = (s) => document.querySelector(s);
  const redraw = () => window.__ttRefresh?.();
  async function slide(step, kicker, title, sub, cam = false) {
    const el = $('#slide');
    el.classList.add('out'); await pause(380);
    $('#kicker').textContent = kicker; $('#title').textContent = title; $('#sub').textContent = sub;
    $('#camcard').hidden = !cam;
    document.querySelectorAll('#steps li').forEach((li, i) => { li.classList.toggle('on', i === step); li.classList.toggle('done', step >= 0 && i < step); });
    el.classList.remove('out');
  }
  async function tap(sel) {
    let el = typeof sel === 'string' ? $(sel) : sel;
    for (let i = 0; !el && i < 30; i++) { await pause(100); el = $(sel); }
    if (!el) { console.warn('demo: not found', sel); return; }
    const r = el.getBoundingClientRect(), f = $('#finger');
    f.style.left = r.left + r.width / 2 + 'px'; f.style.top = r.top + r.height / 2 + 'px';
    f.classList.add('show'); await pause(600);
    f.classList.add('press'); await pause(130); el.click(); await pause(170); f.classList.remove('press');
  }
  async function type(text) {
    const f = $('#askfield');
    for (const ch of text) { f.value += ch; await pause(45 + Math.random() * 40); }
  }
  const hideFinger = () => $('#finger').classList.remove('show');

  async function run() {
    await pause(1500);
    await slide(-1, '', 'A câmara da casa passa a saber onde estão as coisas.', 'O ThingTracker junta-se à aplicação da Altice: regista objetos, encontra-os e responde a perguntas.');
    await pause(4200);

    await slide(0, '1 · Registar', 'Registar a carteira', 'Escolhe-se o objeto e mostra-se à câmara durante alguns segundos.');
    await pause(1600);
    await tap('#tabs button[data-tab="things"]'); await pause(1200);
    await tap('[data-act="add-thing"].btn-p'); await pause(1500);
    await tap('[data-act="pick-thing"][data-name="Wallet"]'); await pause(900);
    hideFinger();
    for (let i = 1; i <= 8; i++) {
      window.DEMO_CAM = `/crops/demo-cam-${((i - 1) % 5) + 1}.jpg`;
      D.boxes = [{ box: [0.16, 0.1, 0.84, 0.9], label: `Registering Wallet · view ${i} of 8`, kind: 'enrol' }];
      D.enrol.got = i; redraw();
      await pause(i === 1 ? 1100 : 820);
    }
    D.boxes = [];
    const w = D.things.find((t) => t.id === 'wallet');
    w.fingerprint = { n: 8, crops: ['demo-view-1.jpg', 'demo-view-2.jpg', 'demo-view-3.jpg', 'demo-view-4.jpg'], created: Date.now() / 1000 };
    D.enrol = null; addEvent('thing', 'Wallet registered: a visual fingerprint from 8 views.');
    redraw(); await pause(2800);
    await tap('.bottom-bar [data-act="finish"]'); await pause(1200);
    hideFinger();

    await slide(1, '2 · Encontrar', 'A câmara encontra-a sozinha', 'Quando há movimento, os modelos em casa procuram a carteira e reconhecem a sua.', true);
    await pause(1400);
    $('#cambox').hidden = false;
    await pause(1100);
    w.last_seen = { ts: today(15, 2), zone_name: 'hall table', room: 'Work Room', where: 'recognised as yours (0.84)', crop: 'demo-seen.jpg' };
    addEvent('seen', 'Wallet seen on the hall table.', { crop: 'demo-seen.jpg' });
    redraw(); await pause(3600);

    await slide(2, '3 · Perguntar', '“Onde está a carteira?”', 'O assistente, em todos os separadores, responde com o lugar, a hora e a fotografia.');
    $('#cambox').hidden = true;
    await pause(1000);
    await tap('#fab'); await pause(1100);
    hideFinger();
    await type('Where is my wallet?'); await pause(500);
    await tap('[data-act="send"]'); await pause(3800);
    hideFinger();

    await slide(3, '4 · Avisar', 'Uma frase cria um sensor', 'O modelo de linguagem converte-a numa regra, avaliada em casa, com as ações pelo MCP da Altice.');
    await pause(900);
    await type('Tell me if I leave home without my wallet'); await pause(500);
    await tap('[data-act="send"]'); await pause(3800);
    await tap('[data-act="close-sheet"]'); await pause(900);
    hideFinger();
    await slide(3, '4 · Avisar', 'A casa avisa', 'A porta abre e a carteira ficou na mesa da entrada: chega uma notificação com a fotografia.');
    await pause(1200);
    addEvent('alert', 'The front door opened and your wallet is still on the hall table.', { title: 'Left without the wallet', crop: 'demo-seen.jpg' });
    redraw(); await pause(5200);

    await slide(-1, 'Equipa IT-Porto · Desafio Altice Labs #3', 'ThingTracker', 'Ver, perceber, lembrar e agir, com a câmara que a casa já tem.');
    document.querySelectorAll('#steps li').forEach((li) => { li.classList.remove('on'); li.classList.add('done'); });
    await pause(4500);
    window.DEMO_DONE = true;
  }
  window.addEventListener('load', () => setTimeout(run, 400));
})();
