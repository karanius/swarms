import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {parseFlowImport} from '../langflow-adapter/import-flow.mjs';
const manifest=JSON.parse(await readFile(new URL('../official-templates.json',import.meta.url),'utf8'));
test('official catalog retains immutable source identity and unverified status',()=>{
 assert.ok(manifest.items.length>0);assert.equal(new Set(manifest.items.map(i=>i.id)).size,manifest.items.length);
 for(const item of manifest.items){assert.match(item.source.revision,/^[a-f0-9]{40}$/);assert.equal(item.source.revision,manifest.sourceRevision);assert.equal(item.validationStatus,'unverified');assert.equal(item.classificationStatus,'unreviewed');assert.equal(item.source.license,'MIT');assert.ok(item.source.url.startsWith('https://github.com/langflow-ai/langflow/blob/'+manifest.sourceRevision+'/'));}
});
test('every downloaded template is byte-identical to its pinned Git blob and structurally importable',async()=>{
 for(const item of manifest.items){const bytes=await readFile(new URL('../../public'+item.file,import.meta.url));assert.equal(createHash('sha256').update(bytes).digest('hex'),item.source.sha256,item.name);assert.equal(createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex'),item.source.gitBlobSha,item.name);const flow=parseFlowImport(bytes.toString());assert.equal(flow.data.nodes.length,item.nodeCount);assert.equal(flow.data.edges.length,item.edgeCount);}
});
test('upstream MIT attribution accompanies the collection',async()=>{const license=await readFile(new URL('../../public/langflow-templates/official/LICENSE',import.meta.url),'utf8');assert.match(license,/MIT License/);assert.match(license,/Copyright .*Langflow/);});
