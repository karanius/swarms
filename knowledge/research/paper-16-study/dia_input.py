"""Documented Dia speaker formatting; never change the requested spoken words."""
import re

def format_input(text,reference=None):
 text=text.strip()
 if not text:raise ValueError('Dia requires spoken text')
 if reference:
  if text.startswith('[S1]'):text=text[4:].strip()
  ref=reference.strip()
  if not ref.startswith('[S1]'):ref='[S1] '+ref
  combined=ref+' '+text
 else:
  if not text.startswith('[S1]'):text='[S1] '+text
  ref=None;combined=text
 tags=re.findall(r'\[S[12]\]',combined)
 if any(a==b for a,b in zip(tags,tags[1:])):raise ValueError('Dia speaker tags must alternate; repeated same-speaker turns should be merged')
 closing='[S2]' if tags[-1]=='[S1]' else '[S1]'
 if not re.search(r'\[S[12]\]\s*$',text):text+=' '+closing
 return text,ref
