const fs = require('fs');
const txt = fs.readFileSync('error_log.txt', 'utf16le');
const idx = txt.indexOf('error during build:');
if (idx !== -1) {
    console.log(txt.substring(idx, idx + 2000));
} else {
    // try to find where the error actually starts
    const lines = txt.split('\n');
    console.log(lines.filter(l => l.includes('error') || l.includes('Error') || l.includes('client.ts')).join('\n').substring(0, 2000));
}
