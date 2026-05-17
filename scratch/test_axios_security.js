import http from 'http';
import axios from 'axios';
import shouldBypassProxy from '../node_modules/axios/lib/helpers/shouldBypassProxy.js';

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS PROXY BYPASS AUDIT");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

// Set proxy configuration in environment
process.env.HTTP_PROXY = 'http://127.0.0.1:5300';
process.env.NO_PROXY = 'localhost,127.0.0.1,::1';

const testHosts = [
  'localhost',
  'localhost.',
  '127.0.0.1',
  '127.0.0.2',
  '127.0.0.100',
  '127.255.255.254',
  '::1',
  '[::1]',
  '::ffff:127.0.0.1',
  '::ffff:7f00:1',
  '0:0:0:0:0:0:0:1'
];

let failed = false;

testHosts.forEach(host => {
  // Wrap raw IPv6 hosts (containing colons and not already bracketed) in brackets for URL parsing
  const isRawIPv6 = host.includes(':') && !host.startsWith('[');
  const formattedHost = isRawIPv6 ? `[${host}]` : host;
  const url = `http://${formattedHost}/secret`;
  const bypassed = shouldBypassProxy(url);
  
  // Every one of these loopbacks MUST bypass the proxy
  if (bypassed) {
    console.log(`  [SAFE]   ${host.padEnd(20)} -> Proxy bypassed (DIRECT connection)`);
  } else {
    console.log(`  [FAILED] ${host.padEnd(20)} -> routed through proxy (SECURITY VULNERABILITY!)`);
    failed = true;
  }
});

console.log("\n======================================================");
if (failed) {
  console.log("  AUDIT FAILED: Loopback address bypasses exist!");
  process.exit(1);
} else {
  console.log("  AUDIT PASSED: All loopback subnets securely bypassed proxy.");
  process.exit(0);
}
