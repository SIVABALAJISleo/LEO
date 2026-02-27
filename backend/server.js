import express from 'express';
import { HyperLogLog } from '../probabilistic/hll.js';
import { BloomFilter } from '../probabilistic/bloom.js';
import { OptimisticSync } from '../optimistic/sync.js';

const app = express();
app.use(express.json());

// Initialize engines
const hll = new HyperLogLog();
const bloom = new BloomFilter();
const sync = new OptimisticSync("demo-user");

app.get('/health', (req, res) => {
    res.json({ status: 'healthy', engine: 'Node-Probabilistic' });
});

// Probabilistic APIs
app.post('/api/approx/count', (req, res) => {
    const { item } = req.body;
    if (item) hll.add(item);
    res.json({ count: hll.count() });
});

app.post('/api/approx/check', (req, res) => {
    const { item, add } = req.body;
    if (add) bloom.add(item);
    const exists = bloom.check(item);
    res.json({ exists });
});

// Optimistic Events (Mocked endpoint for sync visibility)
app.post('/api/sync/update', (req, res) => {
    const { key, value } = req.body;
    sync.applyChange(key, value);
    res.json({ status: 'queued', current_state: sync.getState() });
});

const PORT = 8081;
app.listen(PORT, () => {
    console.log(`Node backend running on port ${PORT}`);
});
