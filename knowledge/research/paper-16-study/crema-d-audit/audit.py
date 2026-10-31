"""Pinned CREMA-D metadata audit. Rankings are candidates, not listening judgments."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,hashlib,io,json,math,urllib.request
S=Path(__file__).resolve().parent
CODES={'ANG':'A','DIS':'D','FEA':'F','HAP':'H','NEU':'N','SAD':'S'}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Paper16-reference-audit'}),timeout=60) as r:return r.read()
def wilson(k,n):
 z=1.96;p=k/n;return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
def decode(row):
 key=int(row['']);mode=key//100000;clip=key%100000
 if mode not in [1,2,3] or clip<1:raise ValueError('Invalid modality/clip key')
 counts={c:int(row[c]) for c in 'ADFHNS'};n=int(row['numResponses'])
 if n<=0 or sum(counts.values())!=n:raise ValueError('Vote count mismatch')
 maximum=max(counts.values());winners=[c for c,v in counts.items() if v==maximum]
 if abs(maximum/n-float(row['agreement']))>1e-10:raise ValueError('Agreement mismatch')
 if set(row['emoVote'].split(':'))!=set(winners):raise ValueError('Tie/majority mismatch')
 actor,sentence,intended,intensity=row['fileName'].split('_');target=CODES[intended]
 means={c:(None if float(row[k])==-1 else float(row[k])) for c,k in zip('ADFHNS',['meanAngerResp','meanDisgustResp','meanFearResp','meanHappyResp','meanNeutralResp','meanSadResp'])}
 for c,v in counts.items():
  if (v==0)!=(means[c] is None):raise ValueError('Missing conditional intensity mismatch')
 return {'file':row['fileName'],'actor':actor,'sentence':sentence,'intended':target,'intended_intensity':intensity,'modality':mode,'clip_number':clip,'counts':counts,'n':n,'majority':winners,'agreement':maximum/n,'target_share':counts[target]/n,'target_wilson_lower':wilson(counts[target],n),'perceived_intensity_given_emotion':means,'overall_intensity':float(row['meanEmoResp']),'eligible_candidate':n>=7 and winners==[target] and counts[target]/n>=.6}
def run():
 manifest=S/'source-manifest.json'
 if manifest.exists():meta=json.loads(manifest.read_text());revision=meta['revision']
 else:
  revision=json.loads(get('https://api.github.com/repos/CheyneyComputerScience/CREMA-D/commits/master'))['sha'];meta={'repository':'https://github.com/CheyneyComputerScience/CREMA-D','revision':revision,'files':{}}
 files=['processedResults/tabulatedVotes.csv','processedResults/summaryTable.csv','SentenceFilenames.csv','VideoDemographics.csv','tabulateVotesV2.r','README.md','LICENSE.txt']
 data={}
 for name in files:
  url=f'https://raw.githubusercontent.com/CheyneyComputerScience/CREMA-D/{revision}/{name}';target=S/name.replace('/','--')
  if not target.exists():target.write_bytes(get(url))
  raw=target.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if name in meta['files'] and meta['files'][name]['sha256']!=sha:raise ValueError('Pinned metadata changed')
  meta['files'][name]={'url':url,'sha256':sha,'bytes':len(raw)};data[name]=raw.decode('utf-8-sig')
 manifest.write_text(json.dumps(meta,indent=2))
 rows=[decode(r) for r in csv.DictReader(io.StringIO(data[files[0]]))]
 index={(r['modality'],r['clip_number']):r for r in rows}
 if len(index)!=len(rows):raise ValueError('Duplicate modality/clip')
 filenames=list(csv.DictReader(io.StringIO(data['SentenceFilenames.csv'])))
 for r in rows:
  if filenames[r['clip_number']-1]['Filename']!=r['file']:raise ValueError('Filename join mismatch')
 summary=list(csv.DictReader(io.StringIO(data['processedResults/summaryTable.csv'])))
 lookup={r['file']:r for r in rows if r['modality']==1}
 for r in summary:
  if set(r['VoiceVote'].split(':'))!=set(lookup[r['FileName']]['majority']):raise ValueError('Voice summary mismatch')
 actors=defaultdict(list)
 for r in lookup.values():actors[r['actor']].append(r)
 ranks=[]
 for actor,clips in actors.items():
  eligible=[r for r in clips if r['eligible_candidate']];coverage={e:sum(r['intended']==e for r in eligible) for e in 'ADFHNS'}
  best={e:sorted([r for r in eligible if r['intended']==e],key=lambda x:(x['target_wilson_lower'],x['n']),reverse=True)[:3] for e in 'ADFHNS'}
  floor=min((best[e][0]['target_wilson_lower'] if best[e] else 0) for e in best)
  ranks.append({'actor':actor,'total_clips':len(clips),'eligible_clips':len(eligible),'eligible_per_emotion':coverage,'all_six':all(coverage.values()),'minimum_best_reference_wilson':floor,'candidate_references':best})
 ranks.sort(key=lambda r:(r['all_six'],r['minimum_best_reference_wilson'],r['eligible_clips']),reverse=True)
 disagreements=sum(set(r['majority'])!=set(index[(3,r['clip_number'])]['majority']) for r in lookup.values())
 report={'revision':revision,'total_modality_rows':len(rows),'clips':len(lookup),'actors':len(actors),'modes':dict(Counter(r['modality'] for r in rows)),'audio_ties':sum(len(r['majority'])>1 for r in lookup.values()),'audio_intended_majority_match':sum(r['majority']==[r['intended']] for r in lookup.values()),'audio_visual_majority_disagreements':disagreements,'candidate_policy':{'minimum_votes':7,'minimum_target_share':.6,'unique_majority_matches_intended':True,'ranking':'maximise weakest-emotion best candidate Wilson lower bound; then eligible count','qualification':'NOT a validated quality threshold or emotion probability'},'ranked_actors':ranks,'example':lookup['1001_IEO_HAP_LO'],'limitations':['Metadata only; audio not downloaded or auditioned','Intensity values are conditional rater judgments, not TTS controls','Wilson intervals assume independent binomial votes; shared raters and selection limit interpretation','Audio-only perception ratings do not prove transfer to novel speech','No actor/voice imitation commercial clearance asserted']}
 (S/'audit-results.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['ranked_actors']},indent=2));print('TOP CANDIDATES',[(r['actor'],r['eligible_per_emotion'],round(r['minimum_best_reference_wilson'],3)) for r in ranks[:5]])
if __name__=='__main__':run()
