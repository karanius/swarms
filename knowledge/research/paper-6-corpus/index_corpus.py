#!/usr/bin/env python3
"""Read-only static corpus indexing. Never imports or executes collected code."""
import csv,datetime,hashlib,json,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def walk(v,pointer='$',depth=0):
 if depth>80:return
 if isinstance(v,dict):
  if 'nodes' in v or 'edges' in v:
   if isinstance(v.get('nodes'),list) and isinstance(v.get('edges'),list):
    yield pointer,v
  for k,x in v.items():yield from walk(x,pointer+'/'+str(k).replace('~','~0').replace('/','~1'),depth+1)
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from walk(x,pointer+'/'+str(i),depth+1)
 elif isinstance(v,str) and len(v)>20 and v.lstrip().startswith(('{','[')) and '"nodes"' in v and '"edges"' in v:
  try:yield from walk(json.loads(v),pointer+'/<encoded-json>',depth+1)
  except (ValueError,RecursionError):pass

def malformed_shapes(v,depth=0):
 if depth>80:return 0
 if isinstance(v,dict):return int('nodes' in v and 'edges' in v and not (isinstance(v['nodes'],list) and isinstance(v['edges'],list)))+sum(malformed_shapes(x,depth+1) for x in v.values())
 if isinstance(v,list):return sum(malformed_shapes(x,depth+1) for x in v)
 return 0

def describe(pointer,g):
 nodes,edges=g['nodes'],g['edges'];ids={};types=[];issues=[];langflow=0;flowise=0;unknown=0
 for n in nodes:
  if not isinstance(n,dict):issues.append('non-object-node');continue
  nid=n.get('id');d=n.get('data',{});d=d if isinstance(d,dict) else {}
  schema=d.get('node')
  if isinstance(schema,dict) and isinstance(schema.get('template'),dict):langflow+=1
  elif (isinstance(d.get('inputAnchors'),list) and isinstance(d.get('outputAnchors'),list)) or (n.get('type')=='agentFlow' and 'inputParams' in d):flowise+=1
  elif n.get('type')!='noteNode':unknown+=1
  typ=str(d.get('type') or n.get('type') or 'unknown')
  types.append(typ)
  if nid is None:issues.append('missing-node-id')
  elif str(nid) in ids:issues.append('duplicate-node-id')
  else:ids[str(nid)]=typ
 links=[]
 for e in edges:
  if not isinstance(e,dict):issues.append('non-object-edge');continue
  s,t=str(e.get('source')),str(e.get('target'))
  if s not in ids or t not in ids:issues.append('dangling-or-missing-endpoint')
  links.append((ids.get(s,'unknown'),ids.get(t,'unknown')))
 sig=json.dumps({'types':sorted(collections.Counter(types).items()),'typedDirectedEdges':sorted(collections.Counter(links).items())},sort_keys=True,separators=(',',':'))
 formatLabel='mixed-langflow-flowise' if langflow and flowise else 'flowise' if flowise else 'langflow' if langflow else 'unknown'
 return {'format':formatLabel,'formatEvidence':{'langflowTemplateNodes':langflow,'flowiseAnchorNodes':flowise,'unknownNonNoteNodes':unknown},'pointer':pointer,'nodeCount':len(nodes),'edgeCount':len(edges),'empty':not nodes and not edges,'structuralIssues':dict(collections.Counter(issues)),'componentTypeCounts':dict(sorted(collections.Counter(types).items())),'typedTopologyHeuristic':hashlib.sha256(sig.encode()).hexdigest()}

def license_info(a,base):
 lic=a.get('license');refs=[]
 if isinstance(lic,dict):refs=lic.get('references',lic.get('files',[])) or []
 texts=[]
 for ref in refs:
  p=base/ref
  if p.is_file():texts.append(p.read_text(errors='replace')[:250000])
 label=(lic.get('spdx') if isinstance(lic,dict) else None) or 'unknown'
 if label in ('NOASSERTION','NONE'):label='unknown'
 return {'label':label,'declared':lic if lic is not None else 'unknown','localReferences':[str((base/r).relative_to(ROOT)) for r in refs if (base/r).is_file()],'missingReferences':[r for r in refs if not (base/r).is_file()],'licenseTextPresent':bool(texts),'reviewRequired':True}

def main():
 rows=[];collectors=[];failures=[];snapshot=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for mp in sorted((ROOT/'collectors').glob('*/manifest.json')):
  try:
   manifestBytes=mp.read_bytes();m=json.loads(manifestBytes)
  except Exception as e:failures.append({'manifest':str(mp.relative_to(ROOT)),'error':type(e).__name__});continue
  collectors.append({'collector':m.get('collector',mp.parent.name),'manifest':str(mp.relative_to(ROOT)),'manifestSha256':hashlib.sha256(manifestBytes).hexdigest(),'sources':m.get('sources',[]),'queries':m.get('queries',[]),'artifactCount':len(m.get('artifacts',[])),'failures':m.get('failures',[]),'otherCoverageMetadata':{k:v for k,v in m.items() if k not in ('collector','sources','queries','artifacts','failures')}})
  for i,a in enumerate(m.get('artifacts',[])):
   row={**a,'collector':m.get('collector',mp.parent.name),'manifest':str(mp.relative_to(ROOT)),'manifestArtifactIndex':i,'file':str((mp.parent/(a.get('file') or '__missing_file__')).relative_to(ROOT)),'licenseAssessment':license_info(a,mp.parent),'graphs':[],'malformedGraphShapeCount':0}
   issues=[]
   for key in ('file','sha256','sourceUrl','sourcePath','collectedAt','license'):
    if key not in a or a[key] is None or a[key]=='':issues.append('missing-'+key)
   if not re.match(r'^https?://',str(a.get('sourceUrl',''))):issues.append('invalid-source-url')
   if not re.fullmatch(r'[a-fA-F0-9]{64}',str(a.get('sha256',''))):issues.append('invalid-sha256')
   row['provenanceIssues']=issues;row['sourceBacked']=not issues
   row['repository']=a.get('repository') or None;row['revision']=a.get('revision') or None
   row['repositoryStatus']='recorded' if row['repository'] else 'unknown-or-not-applicable'
   row['revisionStatus']='recorded' if row['revision'] else 'unknown-or-not-applicable'
   p=ROOT/row['file'];row['fixture']=a.get('collectionKind')=='test-fixture' or bool(re.search(r'(^|/)(tests?|fixtures?|__tests__|__fixtures__)(/|$)',a.get('sourcePath',''),re.I))
   if not p.is_file():row['status']='missing-file'
   else:
    b=p.read_bytes();row['verifiedSha256']=hashlib.sha256(b).hexdigest();row['bytes']=len(b)
    if row['verifiedSha256']!=a.get('sha256'):row['status']='hash-mismatch'
    else:
     try:
      t=b.decode('utf-8-sig');documents=[]
      if p.suffix in ('.md','.mdx'):
       for block in re.findall(r'```(?:json|JSON)?\s*\n(.*?)```',t,re.S):
        try:documents.append(json.loads(block))
        except ValueError:pass
      else:documents=[json.loads(t)]
      for j,d in enumerate(documents):
       row['graphs'].extend(describe(ptr,g) for ptr,g in walk(d,'$' if len(documents)==1 else f'$fence/{j}'));row['malformedGraphShapeCount']+=malformed_shapes(d)
      row['status']='graph-artifact' if any(not g['empty'] for g in row['graphs']) else 'empty-graph-artifact' if row['graphs'] else 'malformed-graph-shape' if row['malformedGraphShapeCount'] else 'no-recognized-graph'
     except (ValueError,UnicodeError,RecursionError):row['status']='malformed-json-or-encoding'
   if row['status'] in ('missing-file','hash-mismatch'):
    row['provenanceIssues'].append(row['status']);row['sourceBacked']=False
   formats={g['format'] for g in row['graphs'] if not g['empty']}
   row['graphFormat']='langflow' if formats=={'langflow'} else 'flowise' if formats=={'flowise'} else 'unknown' if not formats or formats=={'unknown'} else 'mixed-or-ambiguous'
   row['miningEligible']=bool(row['sourceBacked'] and row['status']=='graph-artifact' and row['graphFormat']=='langflow' and not row['fixture'] and not row['malformedGraphShapeCount'] and not any(g['structuralIssues'] or g['formatEvidence']['unknownNonNoteNodes'] for g in row['graphs']))
   row['miningEligibilityMeaning']='Static schema candidate only; does not establish permission, independence, execution validity, or validated composite status.'
   rows.append(row)
 groups=collections.defaultdict(list)
 for i,r in enumerate(rows):
  if r.get('verifiedSha256')==r.get('sha256'):groups[r['sha256']].append(i)
 duplicates=[{'sha256':h,'artifactIndices':v,'provenanceCount':len(v)} for h,v in groups.items() if len(v)>1]
 stats={'artifacts':len(rows),'statusCounts':dict(collections.Counter(r['status'] for r in rows)),'graphFormatCounts':dict(collections.Counter(r['graphFormat'] for r in rows)),'miningEligibleStaticCandidates':sum(r['miningEligible'] for r in rows),'uniqueLangflowVerifiedByteContents':len({r['sha256'] for r in rows if r['graphFormat']=='langflow' and r.get('verifiedSha256')==r.get('sha256')}),'uniqueMiningEligibleByteContents':len({r['sha256'] for r in rows if r['miningEligible']}),'verifiedArtifacts':sum(len(v) for v in groups.values()),'uniqueVerifiedByteContents':len(groups),'duplicateByteGroups':len(duplicates),'duplicateProvenanceRecordsBeyondFirst':sum(len(x['artifactIndices'])-1 for x in duplicates),'provenanceCompleteArtifacts':sum(r['sourceBacked'] for r in rows),'provenanceIncompleteArtifacts':sum(not r['sourceBacked'] for r in rows),'sourceBackedVerifiedArtifacts':sum(r['sourceBacked'] and r.get('verifiedSha256')==r.get('sha256') for r in rows),'unknownRevisionArtifacts':sum(not r.get('revision') for r in rows),'fixtureArtifacts':sum(r['fixture'] for r in rows),'nonfixtureArtifacts':sum(not r['fixture'] for r in rows),'recognizedGraphObjects':sum(len(r['graphs']) for r in rows),'nonemptyGraphObjects':sum(not g['empty'] for r in rows for g in r['graphs']),'malformedGraphShapes':sum(r['malformedGraphShapeCount'] for r in rows),'malformedJsonArtifacts':sum(r['status']=='malformed-json-or-encoding' for r in rows),'emptyGraphObjects':sum(g['empty'] for r in rows for g in r['graphs']),'graphObjectsWithStructuralIssues':sum(bool(g['structuralIssues']) for r in rows for g in r['graphs']),'licenseLabels':dict(collections.Counter(r['licenseAssessment']['label'] for r in rows))}
 result={'schemaVersion':1,'generatedAt':snapshot,'scope':'Static collection inventory only; not rule mining, semantic validation, or promotion to composite components.','counts':stats,'collectors':collectors,'artifacts':rows,'exactByteDuplicateGroups':duplicates,'indexFailures':failures,'topologyCaveat':'typedTopologyHeuristic hashes only component-type and directed type-pair multiplicities; collisions are expected. Equality does not establish graph isomorphism, behavioral equivalence, family membership, or independent production usage.'}
 (ROOT/'index.json').write_text(json.dumps(result,indent=2)+'\n')
 fields=['collector','file','status','sha256','repository','revision','sourcePath','sourceUrl','collectionKind','fixture','graphFormat','miningEligible','bytes','graphCount','nodeCount','edgeCount','licenseLabel']
 with (ROOT/'index.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rows:w.writerow({**{k:r.get(k) for k in fields},'graphCount':len(r['graphs']),'nodeCount':sum(g['nodeCount'] for g in r['graphs']),'edgeCount':sum(g['edgeCount'] for g in r['graphs']),'licenseLabel':r['licenseAssessment']['label']})
 provenanceFields=['artifactIndex','collector','file','sourceUrl','sourcePath','repository','revision','repositoryStatus','revisionStatus','collectedAt','sha256','license','licenseLabel','sourceBacked','provenanceIssues']
 with (ROOT/'sources.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=provenanceFields);w.writeheader()
  for i,r in enumerate(rows):
   record={k:r.get(k) for k in provenanceFields};record.update(artifactIndex=i,repository=r.get('repository') or 'unknown',revision=r.get('revision') or 'unknown',license=json.dumps(r.get('license','unknown'),ensure_ascii=False),licenseLabel=r['licenseAssessment']['label'],provenanceIssues=json.dumps(r['provenanceIssues']))
   w.writerow(record)
 coverage='\n'.join(f"| {c['collector']} | {c['artifactCount']} | {len(c['sources'])} | {len(c['failures'])} |" for c in collectors)
 report=f'''# Langflow static corpus inventory

Snapshot: {snapshot}. Rerun with `python3 knowledge/research/paper-6-corpus/index_corpus.py` from the repository root. This script only reads raw artifacts and manifests and rewrites derived inventory outputs. Collector manifests may continue growing; their snapshot hashes are recorded in the index.

**{stats['artifacts']} provenance records; {stats['uniqueVerifiedByteContents']} distinct verified byte contents.** There are {stats['duplicateByteGroups']} exact-byte duplicate groups and {stats['duplicateProvenanceRecordsBeyondFirst']} provenance records beyond the first copy. Copies retain every source record. These are source graph artifacts, not a count of independent production templates.

| Collector | Artifact records | Source records | Reported failures |
| --- | ---: | ---: | ---: |
{coverage}

## Static inspection

'''+ '\n'.join(f'- {k}: {v}' for k,v in stats.items())+'''

`index.json` contains complete source records, collector queries, all collector-reported failures, caps, inaccessible sources, and coverage metadata. `index.csv` is the compact artifact inventory. `sources.csv` records every item origin, including every exact-byte duplicate; unknown repository/revision/license stays explicit. Mandatory provenance checks require the local file reference, original URL/path, collection time, SHA256, and license metadata. Items failing these checks are flagged and excluded from the source-backed count. Official collector coverage is detailed in `collectors/official/REPORT.md`; other collector reports supply their collection limits. Licenses without collected text or explicit metadata remain unknown; public accessibility does not establish reuse permission. SPDX labels are copied only from explicit collector declarations; no license identity is inferred from accessibility or text. Collected license references and missing references are recorded for review; no code/content licensing conclusion is made.

## Recognition and limitations

Graph-shaped objects are recognized recursively as objects containing both `nodes` and `edges` arrays, including nested exported flows and JSON-encoded strings. Langflow format requires node.data.node.template dictionary evidence. Flowise format is identified by its input/output-anchor schema or agentFlow input schema; mixed and unknown formats remain explicit. Format evidence counts are retained per graph. Empty graphs are recorded separately. The miningEligible flag is only a conservative static candidate flag: it excludes Flowise, mixed/unknown formats, fixtures, missing provenance, structural problems, and unknown non-note node schemas; it does not validate behavior, rights, independence, or component boundaries. Invalid JSON, missing files, hash mismatches, and files without recognized graphs have explicit statuses. Graphs with non-object nodes/edges, missing or duplicated node IDs, or dangling edge endpoints retain structural issue counts. Fixture classification uses source path and collector metadata; it is a provenance hint, not a production-status determination. Component configuration, credentials, and code values are never printed by this indexer.

The optional typed topology hash includes component-type counts and directed type-pair counts only. It is deliberately lossy: matching hashes are merely candidates for later inspection, not graph isomorphism, semantic equivalence, independent templates, or validated composite boundaries. Exact-byte identity also does not establish independent authorship. Counts do not estimate completeness across the internet. Undiscovered, removed, private, rate-limited, capped, dynamically generated, or nonstandard exports remain outside measured coverage.

Downloaded component code was never imported, evaluated, or executed. Raw files remain immutable and local. This inventory performs no rule mining. Methods papers and reading notes are in `methods/`; paper hashes and primary URLs are in its manifest.
'''
 report+='\n## Reported inaccessible sources, failures, and limits\n\n'
 for c in collectors:
  report+=f"\n### {c['collector']}\n\n"
  if not c['failures']:report+='No collector-reported failures at this snapshot.\n'
  for f in c['failures']:
   report+='- '+json.dumps(f,ensure_ascii=False,separators=(', ', ': ')).replace('\n',' ')+'\n'
  capped=[]
  for source in c['sources']:
   if source.get('treeTruncated') or source.get('jsonCandidates',0)>source.get('jsonCandidatesExamined',source.get('jsonCandidates',0)) or any(k.lower() in ('skipped','capped','limitreached') and v for k,v in source.items()):capped.append(source)
  for source in capped:report+='- Capped/truncated source: '+json.dumps(source,ensure_ascii=False,separators=(', ', ': '))+'\n'
 report+='\n## Methods papers\n\n'
 methodManifest=ROOT/'methods/manifest.json'
 if methodManifest.is_file():
  for paper in json.loads(methodManifest.read_text()):
   paperPath=ROOT/'methods'/paper.get('file','missing')
   verified=paperPath.is_file() and hashlib.sha256(paperPath.read_bytes()).hexdigest()==paper.get('sha256')
   report+=f"- [{paper.get('title','Unknown title')}]({paper.get('sourceUrl','')}): local `{paper.get('file')}`, SHA256 `{paper.get('sha256')}`, verified={verified}; notes `{paper.get('notes')}`.\n"
 report+='\nThe public-catalog collector explicitly excludes 18 Flowise-format files retained only as local evidence; its manifest is authoritative. Hugging Face HTTP 429 metadata failures are gaps; no rate-limit bypass was attempted.\n'
 (ROOT/'CORPUS_REPORT.md').write_text(report)
 print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
