// Exercise the actual runner transport with an unresponsive/disconnecting Chrome peer.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync('scripts/capture_globe_browser_evidence.mjs', 'utf8');
const connectCdp = new Function(`${source.slice(source.indexOf('async function connectCdp('), source.indexOf('async function evaluate('))}; return connectCdp;`)();
class FakeSocket extends EventTarget {
  static opens = true;
  constructor() {
    super(); FakeSocket.latest = this;
    if (FakeSocket.opens) queueMicrotask(() => this.dispatchEvent(new Event('open')));
  }
  send(data) { this.request = JSON.parse(data); }
  close() { this.dispatchEvent(new Event('close')); }
  reply(result) { this.dispatchEvent(new MessageEvent('message', {data: JSON.stringify({id: this.request.id, result})})); }
}
global.WebSocket = FakeSocket;
(async () => {
  FakeSocket.opens = false;
  await assert.rejects(connectCdp('ws://test', Date.now() + 30), /Timed out connecting/);
  FakeSocket.opens = true;
  const client = await connectCdp('ws://test', Date.now() + 100);
  const response = client.send('Page.enable');
  FakeSocket.latest.reply({enabled: true});
  assert.deepEqual(await response, {enabled: true});
  await assert.rejects(client.send('Runtime.evaluate'), /Timed out.*Runtime.evaluate/);
  client.close();
  const closed = await connectCdp('ws://test', Date.now() + 1000);
  const waiting = closed.send('Page.navigate');
  closed.close();
  await assert.rejects(waiting, /WebSocket closed/);
  console.log('CDP deadline, response and disconnect checks PASS');
})().catch(error => {console.error(error); process.exitCode = 1;});
