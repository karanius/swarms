"""English sentence-boundary gate for new character targets, not a grammar grader."""
import pysbd
VERSION='one-sentence-v1'
def inspect(text):
 text=str(text or '').strip()
 sentences=[s.strip() for s in pysbd.Segmenter(language='en',clean=False).segment(text) if s.strip()]
 error=None
 if not 5<=len(text)<=500:error='Enter one sentence between 5 and 500 characters.'
 elif len(sentences)!=1:error='Use exactly one sentence per take; found '+str(len(sentences))+'. Generate each sentence separately.'
 return {'valid':error is None,'text':text,'sentence_count':len(sentences),'sentences':sentences,'error':error,'policy':VERSION,'method':'pySBD 0.3.4, English sentence-boundary detection','limitation':'Detects sentence boundaries; it does not certify grammar or infer missing punctuation.'}
def require(text):
 result=inspect(text)
 if not result['valid']:raise ValueError(result['error'])
 return result['text']
