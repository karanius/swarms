"""Loopback-only UI for the existing Paper 11 engine. No source code execution."""
import json, secrets, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from architecture import ArchitectureDesigner, validate_proposal
from design_adviser import clarification_questions,normalize_context
HOST='127.0.0.1'; PORT=5193
ORIGIN=f'http://{HOST}:{PORT}'
ENGINE=ArchitectureDesigner().engine
SESSIONS={}; LOCK=threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def reply(self,status,data,kind='application/json',cookie=None):
        body=data if isinstance(data,bytes) else json.dumps(data).encode()
        self.send_response(status)
        for k,v in {'Content-Type':kind,'Content-Length':str(len(body)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'"}.items():self.send_header(k,v)
        if cookie:self.send_header('Set-Cookie',cookie)
        self.end_headers();self.wfile.write(body)
    def allowed(self):return self.headers.get('Host')==f'{HOST}:{PORT}'
    def do_GET(self):
        if not self.allowed():return self.reply(403,{'error':'Invalid local host'})
        if self.path=='/':return self.reply(200,Path(__file__).with_name('app').joinpath('index.html').read_bytes(),'text/html; charset=utf-8')
        if self.path=='/api/session':
            token=secrets.token_urlsafe(32)
            with LOCK:
                for key in list(SESSIONS):
                    if time.monotonic()-SESSIONS[key]['time']>86400:del SESSIONS[key]
                if len(SESSIONS)>=100:return self.reply(503,{'error':'Session limit reached; try later'})
                SESSIONS[token]={'designer':ArchitectureDesigner(ENGINE),'lock':threading.Lock(),'time':time.monotonic()}
            return self.reply(200,{'ready':True},cookie=f'paper11={token}; HttpOnly; SameSite=Strict; Path=/')
        return self.reply(404,{'error':'Not found'})
    def do_POST(self):
        if not self.allowed() or self.headers.get('Origin')!=ORIGIN:return self.reply(403,{'error':'Use the local app to submit requests'})
        if self.path not in ('/api/propose','/api/clarify'):return self.reply(404,{'error':'Not found'})
        try:
            if not self.headers.get('Content-Type','').startswith('application/json'):raise ValueError('Expected JSON')
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=24000:raise ValueError('Request is too large or empty')
            cookies=SimpleCookie(self.headers.get('Cookie',''));token=cookies.get('paper11')
            session=SESSIONS.get(token.value if token else '')
            if not session:return self.reply(401,{'error':'Session expired. Reload the app.'})
            data=json.loads(self.rfile.read(length));question=data.get('question')
            if not isinstance(question,str) or not 3<=len(question.strip())<=1000:raise ValueError('Describe your request in 3–1000 characters')
            context=normalize_context(data.get('context'))
            if self.path=='/api/clarify':return self.reply(200,{'questions':clarification_questions(question,context)})
            parent=data.get('parent');excluded=data.get('excluded',[]);reason=data.get('reason')
            if not isinstance(excluded,list) or any(not isinstance(x,str) for x in excluded):raise ValueError('Invalid candidate exclusion')
            with session['lock']:
                d=session['designer']
                if len(d.history())>=40:raise ValueError('Session has 40 revisions. Reload to start a new session.')
                p=d.propose(question.strip(),k=30,parent=parent,excluded_ids=excluded,revision_reason=reason,context=context)
                errors=validate_proposal(p,d.engine)
                if errors:raise RuntimeError('Proposal did not pass its evidence checks')
                session['time']=time.monotonic()
                self.reply(200,{'proposal':p,'history':d.history()})
        except (ValueError,TypeError,json.JSONDecodeError) as e:self.reply(400,{'error':str(e)})
        except Exception:self.reply(503,{'error':'The proposal engine could not finish. Check the local search/model service and try again.'})
if __name__=='__main__':
    print(f'Paper 11 app: {ORIGIN}',flush=True)
    HTTPServer((HOST,PORT),Handler).serve_forever()
