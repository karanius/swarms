import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import pi_adapter
import discovery

class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        connection=patch('pi_adapter.proxy_connection',return_value=({},'instance-proxy/test-model'))
        connection.start()
        self.addCleanup(connection.stop)
        self.instance={'id':'test-instance','outcome':'Find a home in Da Nang'}
        self.state=pi_adapter.initial_state(self.instance)
        self.candidate=dict(self.state,name='Da Nang Home Finder',summary='Find a suitable home.',
             next_question='What is your monthly budget?',recommendation='Set a total monthly ceiling.',
             questions=[{'id':'budget','text':'What is the budget?','depends_on':[]}],
             tower=[{'id':'research','name':'Multi-source research','layer':'Composite Components','status':'proposed','rationale':'Compare housing options against the intent.'}])

    def test_reconstruct_and_project_without_chat_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            state=pi_adapter.validate(self.candidate,self.state)
            discovery.persist(root,self.instance,state)
            self.assertEqual(discovery.load(root,self.instance),state)
            folder=discovery.workspace(root,self.instance)
            self.assertIn('Da Nang',(folder/'INTENT.md').read_text())
            self.assertEqual(json.loads((folder/'tower.json').read_text())['blocks'],state['tower'])

    def test_reject_intent_change_and_implemented_claim(self):
        candidate=copy.deepcopy(self.candidate)
        candidate['intent']='Different intent'
        with self.assertRaises(pi_adapter.PiError):pi_adapter.validate(candidate,self.state)
        candidate=copy.deepcopy(self.candidate)
        candidate['tower'][0]['status']='tested'
        with self.assertRaises(pi_adapter.PiError):pi_adapter.validate(candidate,self.state)

    def test_preserve_confirmed_decisions(self):
        self.state['decisions']=[{'id':'one','text':'Budget is 1000','source':'1000'}]
        with self.assertRaises(pi_adapter.PiError):pi_adapter.validate(self.candidate,self.state)

    def test_reject_dependency_cycle(self):
        candidate=copy.deepcopy(self.candidate)
        candidate['questions']=[{'id':'a','text':'A','depends_on':['b']},{'id':'b','text':'B','depends_on':['a']}]
        with self.assertRaises(pi_adapter.PiError):pi_adapter.validate(candidate,self.state)

    def test_adapter_uses_saved_context_and_no_tools(self):
        response=SimpleNamespace(returncode=0,stdout=json.dumps(self.candidate))
        with patch('pi_adapter.subprocess.run',return_value=response) as invocation:
            result=pi_adapter.propose(self.state)
        args=invocation.call_args
        self.assertIn('--no-tools',args.args[0])
        self.assertIn('--no-session',args.args[0])
        self.assertEqual(json.loads(args.kwargs['input'])['state']['intent'],self.state['intent'])
        self.assertEqual(result['name'],'Da Nang Home Finder')

    def test_cli_accepts_pi_proposal_then_resumes_from_disk(self):
        import instance_builder as ui
        import io
        from rich.console import Console
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            ui.save(root,dict(self.instance,schema_version=1,updated_at='now'))
            with patch.object(ui,'console',Console(file=io.StringIO())), patch('builtins.input',side_effect=['2','1','c','c','a','/back','q']), patch('pi_adapter.propose',return_value=pi_adapter.validate(self.candidate,self.state)):
                ui.run(root)
            loaded=discovery.load(root,self.instance)
            self.assertEqual(loaded['name'],'Da Nang Home Finder')
            with patch.object(ui,'console',Console(file=io.StringIO())), patch('builtins.input',side_effect=['2','1','c','/back','q']), patch('pi_adapter.propose') as provider:
                ui.run(root)
                provider.assert_not_called()

    def test_assistant_defaults_cannot_become_user_decisions(self):
        candidate=copy.deepcopy(self.candidate)
        candidate['decisions']=[{'id':'budget','text':'Budget is 20 million VND','source':'20 million VND'}]
        with patch('pi_adapter.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=json.dumps(candidate))):
            with self.assertRaises(pi_adapter.PiError):
                pi_adapter.propose(self.state,'20 million VND',reply_role='assistant')

    def test_finish_creates_handoff_with_unresolved_work(self):
        with tempfile.TemporaryDirectory() as directory:
            state=pi_adapter.validate(self.candidate,self.state)
            finished=discovery.finish(Path(directory),self.instance,state)
            self.assertEqual(finished['lifecycle'],'design_handoff_ready')
            text=(discovery.workspace(Path(directory),self.instance)/'HANDOFF.md').read_text()
            self.assertIn('What is the budget?',text)
            self.assertIn('research and execution remain open',text)

    def test_provider_failure_keeps_records_unchanged(self):
        with patch('pi_adapter.subprocess.run',return_value=SimpleNamespace(returncode=1,stdout='')):
            with self.assertRaises(pi_adapter.PiError):pi_adapter.propose(self.state)
        self.assertIsNone(self.state['name'])

    def test_unsubstantiated_decision_rejected(self):
        candidate=copy.deepcopy(self.candidate)
        candidate['decisions']=[{'id':'budget','text':'Budget 1000','source':'1000'}]
        with patch('pi_adapter.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout=json.dumps(candidate))):
            with self.assertRaises(pi_adapter.PiError):pi_adapter.propose(self.state,'I prefer a quiet neighborhood')

if __name__=='__main__': unittest.main()

class ProxyConfigurationTests(unittest.TestCase):
    def test_selected_model_becomes_pi_provider(self):
        import io
        with tempfile.TemporaryDirectory() as directory, patch('pi_adapter.ROOT',Path(directory)), patch('pi_adapter.urllib.request.urlopen',return_value=io.BytesIO(json.dumps({'data':[{'id':'chosen-model'}]}).encode())):
            env,model=pi_adapter.proxy_connection()
            config=json.loads((Path(directory)/'.pi-runtime/models.json').read_text())
            self.assertEqual(model,'instance-proxy/chosen-model')
            self.assertEqual(config['providers']['instance-proxy']['api'],'openai-responses')
            self.assertNotIn('OPENAI_API_KEY',config['providers']['instance-proxy'])
