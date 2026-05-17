import http from 'http';
import axios from 'axios';

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS CRLF multipart Injection");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

let receivedBody = '';

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', chunk => { body += chunk.toString(); });
  req.on('end', () => {
    receivedBody = body;
    res.writeHead(200);
    res.end('ok');
  });
});

server.listen(0, '127.0.0.1', async () => {
  const port = server.address().port;

  class SpecFormData {
    constructor() {
      this._entries = [];
      this[Symbol.toStringTag] = 'FormData';
    }
    append(name, value) { this._entries.push([name, value]); }
    [Symbol.iterator]() { return this._entries[Symbol.iterator](); }
    entries() { return this._entries[Symbol.iterator](); }
  }

  const fd = new SpecFormData();

  fd.append('photo', {
    type: 'image/jpeg\r\nX-Injected-Header: PWNED-by-attacker\r\nX-Evil: arbitrary-value',
    size: 17,
    name: 'photo\r\nfilename_escaped.jpg',
    [Symbol.asyncIterator]: async function*() {
      yield Buffer.from('MALICIOUS PAYLOAD');
    }
  });

  try {
    await axios.post(`http://127.0.0.1:${port}/upload`, fd);
    
    console.log("\n-- ANALYZING MULTIPART BODY --");
    
    // A real header injection requires the CRLF sequence \r\n to precede the injected header
    const hasInjectedHeader = receivedBody.includes('\r\nX-Injected-Header: PWNED-by-attacker');
    const hasRawCRLFInFilename = receivedBody.includes('name="photo\r\n');
    const hasEscapedFilename = receivedBody.includes('name="photo%0D%0A');
    
    let passed = 0;
    let failed = 0;
    
    if (hasInjectedHeader) {
      console.log('  [FAILED] CRLF injection into Content-Type succeeded! VULNERABLE.');
      failed++;
    } else {
      console.log('  [SAFE]   CRLF injection into Content-Type was safely blocked.');
      passed++;
    }
    
    if (hasRawCRLFInFilename) {
      console.log('  [FAILED] CRLF injection into Content-Disposition filename succeeded! VULNERABLE.');
      failed++;
    } else if (hasEscapedFilename) {
      console.log('  [SAFE]   CRLF injection in filename was safely escaped to %0D%0A.');
      passed++;
    } else {
      console.log('  [SAFE]   Content-Disposition is clean.');
      passed++;
    }
    
    console.log("\n======================================================");
    const total = passed + failed;
    if (failed === 0) {
      console.log(`  AUDIT PASSED: ${passed}/${total} checks secure. CRLF multipart injection mitigated.`);
      process.exit(0);
    } else {
      console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
      process.exit(1);
    }
  } catch (err) {
    console.error("Error during execution:", err.message);
    process.exit(1);
  } finally {
    server.close();
  }
});
