const assert=require('node:assert/strict'),h=require('../scripts/unified_explorer/runtime.js'),p=require('../fixtures/amboise_context/v1/packet.json');
const b={amboiseContext:p},s={presence_id:p.residence_ref};
for(const year of [1517,1518,1519]){assert.equal(Boolean(h.contextualEvent(b,s,{mode:'scrub',cursorYear:year})),year===1518);assert.equal(Boolean(h.contextualEvent(b,s,{mode:'range',startYear:year,endYear:year})),year===1518);}
assert.equal(h.contextualEvent(b,s,{mode:'range',startYear:1500,endYear:1520}),p);
assert.equal(h.contextualEvent(b,{presence_id:'other'},{mode:'scrub',cursorYear:1518}),null);
assert.throws(()=>h.contextualEvent(b,s,{queryResolution:'day'}));
