export interface AuditRecord {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  resource: string;
  status: "success" | "failure" | "warning";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  metadata: Record<string, any>;
}

export class AuditLogger {
  private static instance: AuditLogger;

  // In production, this would stream to a secure, write-once log server or DB
  private records: AuditRecord[] = [];

  private constructor() {}

  static getInstance(): AuditLogger {
    if (!AuditLogger.instance) {
      AuditLogger.instance = new AuditLogger();
    }
    return AuditLogger.instance;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async log(
    action: string,
    resource: string,
    status: AuditRecord["status"] = "success",
    metadata: Record<string, any> = {},
  ) {
    const record: AuditRecord = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      user: "system-agent", // Should be dynamic in full SaaS
      action,
      resource,
      status,
      metadata,
    };

    this.records.push(record);

    // Immutable-style console logging for proof
    console.info(
      `[AUDIT] [${record.timestamp}] ${record.action} on ${record.resource} - ${record.status.toUpperCase()}`,
    );
  }

  getExport(): string {
    return JSON.stringify(this.records, null, 2);
  }
}
