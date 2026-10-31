import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const template=JSON.parse(readFileSync(new URL('./swift-definition.json',import.meta.url),'utf8'));
test('Swift stays reference-only while scripts own assembly and deployment',()=>{
 assert.equal(template.kind,'agent-template');
 assert.equal(template.runtime,undefined);
 assert.ok(template.assembly.scriptRef.endsWith('assemble-swift.mjs'));
 assert.ok(template.deployment.launcherRef.endsWith('deploy-swift.mjs'));
 assert.equal(template.documents.length,6);
 for(const document of template.documents){
  assert.equal(document.content,undefined);
  const source=readFileSync(new URL('../../public'+document.href,import.meta.url));
  assert.equal(createHash('sha256').update(source).digest('hex'),document.sha256);
 }
 assert.deepEqual(template.architecture.filter(row=>row.tools?.length).map(row=>row.piece),['Library tools']);
});
