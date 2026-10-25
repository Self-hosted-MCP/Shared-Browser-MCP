// The bottom of the search page: just where this connection comes from and whether it is private.
// Read from our own admin API; nothing leaves the server.
(async () => {
  const src = (document.currentScript && document.currentScript.dataset.src) || '/api/security';   // the browser's own copy has no admin API
  const box = document.createElement('div');
  box.id = 'sb-status';
  document.body.append(box);
  const add = (label, value, tip) => {
    const item = document.createElement('div');
    item.className = 'sb-item';
    if (tip) item.title = tip;
    const l = document.createElement('span'); l.className = 'sb-label'; l.textContent = label;
    const v = document.createElement('b'); v.textContent = value;
    item.append(l, v);
    box.append(item);
  };
  let d;
  try {
    const r = await fetch(src, { cache: 'no-store', credentials: 'same-origin' });
    if (!r.ok) throw new Error(r.status);
    d = await r.json();
  } catch (e) { add('Security info', 'not available right now'); return; }

  const x = d.exit;
  add('IP', x ? x.ip : 'unknown', 'Where this server, and its browser, reach the internet from. This is what websites see.');
  add('Country', x ? x.country_name + (x.colo ? ' (' + x.colo + ')' : '') : 'unknown');
  add('Network', x && x.network && x.network.name ? x.network.name : 'unknown', 'Who the address belongs to.');
  const vpn = x && x.network && x.network.vpn;
  add('Protected by VPN', vpn ? 'yes (' + x.network.vpn_name + ')' : 'no',
    'Checked with IVPN’s own lookup and the address name. Other VPNs cannot be detected, so "no" means not detected.');
})();

// On a phone, show the first 10 results and hide the rest behind one button.
(() => {
  const list = [...document.querySelectorAll('#urls article.result, #results article.result')];
  if (list.length <= 10 || !matchMedia('(max-width: 700px)').matches) return;
  const rest = list.slice(10);
  rest.forEach(r => r.hidden = true);
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.id = 'sb-more';
  btn.textContent = 'Show ' + rest.length + ' more';
  btn.onclick = () => { rest.forEach(r => r.hidden = false); btn.remove(); };
  list[9].after(btn);
})();

// On a phone, hide the folding boxes under the results except "Suggestions" and "Info".
(() => {
  if (!matchMedia('(max-width: 700px)').matches) return;
  document.querySelectorAll('details').forEach(d => {
    const t = (d.firstElementChild ? d.firstElementChild.textContent : d.textContent).trim().slice(0, 60);
    if (/response time|search url|download results/i.test(t)) d.style.setProperty('display', 'none', 'important');
  });
})();
