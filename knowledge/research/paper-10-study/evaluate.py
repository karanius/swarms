"""Exposed development benchmark; reference component types are not task-success labels."""
import json, time
from pathlib import Path
from search_engine import CorpusSearch, D

CASES=[
 ('video speech','Which pieces extract spoken words from a video URL?',{'YouTubeTranscripts','YouTubeTranscriptComponent'}),
 ('audience reactions','Which pieces collect viewer comments to understand audience feedback?',{'YouTubeCommentsComponent'}),
 ('competitor profiles','Find company pricing tiers, free trials, target industries and API offerings',{'StructuredOutput','StructuredOutputComponent'}),
 ('page content','Read a webpage address and turn its contents into usable text',{'URLComponent','WebBaseLoader','FirecrawlScrapeApi'}),
 ('document chunks','Split a long document into smaller chunks for retrieval',{'SplitText','RecursiveCharacterTextSplitter'}),
 ('typed output','Turn an answer into typed JSON fields instead of free-form prose',{'StructuredOutput','StructuredOutputComponent'}),
 ('relational query','Query relational tables and return SQL results',{'SQLComponent','SQLDatabase'}),
 ('web evidence','Search the current web for evidence and cite pages',{'UnifiedWebSearch','TavilySearchComponent','GoogleSerperAPICore','Serp'}),
]

def run():
    search=CorpusSearch();rows=[]
    for name,question,expected in CASES:
        for arm in ['filename','field_lexical','hybrid']:
            start=time.monotonic()
            result=search.filename_search(question,k=6) if arm=='filename' else search.search(question,k=6,kind='template',semantic=arm=='hybrid')['results']
            found=any(expected&set(r['component_types']) for r in result)
            rows.append({'case':name,'question':question,'arm':arm,'reference_type_present_at_6':found,'seconds':round(time.monotonic()-start,4),'returned':len(result),'titles':[r['title'] for r in result],'ids':[r['id'] for r in result],'expected_types':sorted(expected)})
    summary={arm:sum(r['reference_type_present_at_6'] for r in rows if r['arm']==arm) for arm in ['filename','field_lexical','hybrid']}
    report={'scope':'Exposed development comparison with eight authored queries. Same template search space and top-six cutoff. Type-presence is a weak retrieval relevance proxy, not semantic correctness, independent evaluation, execution success or measured assembly acceleration.','cases':len(CASES),'hits':summary,'rows':rows}
    (D/'EVALUATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'cases':len(CASES),'hits':summary},indent=2));return report

if __name__=='__main__':run()
