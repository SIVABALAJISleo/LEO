export interface Metric {
    name: string;
    value: number;
    type: 'counter' | 'gauge' | 'histogram';
    tags?: Record<string, string>;
    timestamp: number;
}

export class SystemMetrics {
    private static instance: SystemMetrics;
    private metrics: Metric[] = [];
    private readonly MAX_HISTORY = 5000;

    private constructor() { }

    static getInstance(): SystemMetrics {
        if (!SystemMetrics.instance) {
            SystemMetrics.instance = new SystemMetrics();
        }
        return SystemMetrics.instance;
    }

    increment(name: string, value: number = 1, tags?: Record<string, string>) {
        this.record(name, value, 'counter', tags);
    }

    gauge(name: string, value: number, tags?: Record<string, string>) {
        this.record(name, value, 'gauge', tags);
    }

    histogram(name: string, value: number, tags?: Record<string, string>) {
        this.record(name, value, 'histogram', tags);
    }

    private record(name: string, value: number, type: 'counter' | 'gauge' | 'histogram', tags?: Record<string, string>) {
        this.metrics.push({
            name,
            value,
            type,
            tags,
            timestamp: Date.now()
        });

        if (this.metrics.length > this.MAX_HISTORY) {
            this.metrics.shift();
        }
    }

    getMetrics(name?: string): Metric[] {
        if (name) {
            return this.metrics.filter(m => m.name === name);
        }
        return this.metrics;
    }

    getSummary(): Record<string, any> {
        const summary: Record<string, any> = {};

        // Group by name
        const grouped = this.metrics.reduce((acc, m) => {
            if (!acc[m.name]) acc[m.name] = [];
            acc[m.name].push(m);
            return acc;
        }, {} as Record<string, Metric[]>);

        Object.keys(grouped).forEach(name => {
            const ms = grouped[name];
            const type = ms[0].type;

            if (type === 'counter') {
                summary[name] = ms.reduce((sum, m) => sum + m.value, 0);
            } else if (type === 'histogram') {
                const values = ms.map(m => m.value);
                const sum = values.reduce((a, b) => a + b, 0);
                summary[name] = {
                    count: values.length,
                    avg: sum / values.length,
                    min: Math.min(...values),
                    max: Math.max(...values)
                };
            } else {
                // Gauge - show latest
                summary[name] = ms[ms.length - 1].value;
            }
        });

        return summary;
    }
}
