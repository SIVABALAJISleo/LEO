import * as duckdb from '@duckdb/duckdb-wasm';
import * as arrow from 'apache-arrow';

class DuckDBEngine {
  private db: duckdb.AsyncDuckDB | null = null;

  async init() {
    if (this.db) return;

    const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
    const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

    const worker_url = URL.createObjectURL(
      new Blob([`importScripts("${bundle.mainWorker!}");`], { type: 'text/javascript' })
    );

    const worker = new Worker(worker_url);
    const logger = new duckdb.ConsoleLogger();
    this.db = new duckdb.AsyncDuckDB(logger, worker);
    await this.db.instantiate(bundle.mainModule, bundle.pthreadWorker);
    URL.revokeObjectURL(worker_url);
  }

  async runQuery(sql: string): Promise<any[]> {
    if (!this.db) await this.init();
    const conn = await this.db!.connect();
    try {
      const result = await conn.query(sql);
      return result.toArray().map((row) => row.toJSON());
    } finally {
      await conn.close();
    }
  }

  async registerFile(name: string, url: string) {
    if (!this.db) await this.init();
    await this.db!.registerFileURL(name, url, duckdb.DuckDBDataProtocol.HTTP, false);
  }
}

export const globalDuckDB = new DuckDBEngine();
