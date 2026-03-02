import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Shield, 
  Database, 
  AlertTriangle, 
  Lock, 
  Activity, 
  FileText,
  Play,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw
} from "lucide-react";
import { firebaseClient as supabase } from '@/integrations/firebase/client';
import { useAuth } from "@/contexts/AuthContext";
import { Navbar } from "@/components/Navbar";

interface ProofResult {
  proof_type: string;
  executed_at: string;
  success: boolean;
  evidence: Record<string, unknown>;
  logs: string[];
}

interface ProofHistory {
  id: string;
  created_at: string;
  event_data: ProofResult;
}

const PROOF_CONFIGS = [
  {
    id: "proof_incident_handling",
    name: "Incident Auto-Handling",
    description: "Force failure → detect → recover → log",
    icon: AlertTriangle,
    color: "text-orange-500",
  },
  {
    id: "proof_backup_restore",
    name: "Backup & Restore",
    description: "Create backup → validate → restore drill",
    icon: Database,
    color: "text-blue-500",
  },
  {
    id: "proof_rate_limiting",
    name: "Rate Limiting",
    description: "Burst attack → throttle → block → log",
    icon: Shield,
    color: "text-red-500",
  },
  {
    id: "proof_auth_denial",
    name: "Auth Enforcement",
    description: "Unauthorized request → deny → log 403",
    icon: Lock,
    color: "text-purple-500",
  },
  {
    id: "proof_slo_enforcement",
    name: "SLO Enforcement",
    description: "Exceed error budget → degrade → preserve core",
    icon: Activity,
    color: "text-yellow-500",
  },
  {
    id: "proof_audit_export",
    name: "Audit Log Export",
    description: "Export bundle → hash → verify integrity",
    icon: FileText,
    color: "text-green-500",
  },
];

export default function RuntimeProofs() {
  const { user } = useAuth();
  const [results, setResults] = useState<Record<string, ProofResult | null>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [history, setHistory] = useState<ProofHistory[]>([]);
  const [runningAll, setRunningAll] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    const { data } = await supabase
      .from("analytics_events")
      .select("*")
      .eq("event_type", "runtime_proof")
      .order("created_at", { ascending: false })
      .limit(20);
    
    if (data) {
      setHistory(data.map(d => ({
        id: d.id,
        created_at: d.created_at,
        event_data: d.event_data as unknown as ProofResult,
      })));
    }
  };

  const runProof = async (proofId: string) => {
    setLoading(prev => ({ ...prev, [proofId]: true }));
    
    try {
      const { data, error } = await supabase.functions.invoke("runtime-proof", {
        body: { action: proofId, user_id: user?.id },
      });

      if (error) throw error;
      
      setResults(prev => ({ ...prev, [proofId]: data }));
      fetchHistory();
    } catch (error) {
      console.error(`Error running ${proofId}:`, error);
      setResults(prev => ({
        ...prev,
        [proofId]: {
          proof_type: proofId,
          executed_at: new Date().toISOString(),
          success: false,
          evidence: { error: String(error) },
          logs: [`Error: ${error}`],
        },
      }));
    } finally {
      setLoading(prev => ({ ...prev, [proofId]: false }));
    }
  };

  const runAllProofs = async () => {
    setRunningAll(true);
    
    for (const proof of PROOF_CONFIGS) {
      await runProof(proof.id);
      await new Promise(r => setTimeout(r, 500));
    }
    
    setRunningAll(false);
  };

  const allPassed = PROOF_CONFIGS.every(p => results[p.id]?.success);
  const executedCount = Object.values(results).filter(r => r !== null).length;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8 pt-24">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Runtime Proof Execution</h1>
            <p className="text-muted-foreground mt-1">
              Generate irreversible evidence that the system handles real failures
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <Badge variant={executedCount === PROOF_CONFIGS.length && allPassed ? "default" : "secondary"}>
              {executedCount}/{PROOF_CONFIGS.length} Executed
            </Badge>
            
            <Button 
              onClick={runAllProofs} 
              disabled={runningAll}
              size="lg"
            >
              {runningAll ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Running All...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Run All Proofs
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Final Verdict */}
        {executedCount === PROOF_CONFIGS.length && (
          <Card className={`mb-8 ${allPassed ? "border-green-500 bg-green-500/10" : "border-red-500 bg-red-500/10"}`}>
            <CardContent className="py-6">
              <div className="flex items-center gap-4">
                {allPassed ? (
                  <CheckCircle className="h-12 w-12 text-green-500" />
                ) : (
                  <XCircle className="h-12 w-12 text-red-500" />
                )}
                <div>
                  <h2 className="text-2xl font-bold">
                    {allPassed ? "PRODUCTION-READY" : "NOT READY"}
                  </h2>
                  <p className="text-muted-foreground">
                    {allPassed 
                      ? "All runtime proofs verified. System has exercised real failure recovery."
                      : "Some proofs failed. Review logs and re-run failed proofs."}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Proof Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {PROOF_CONFIGS.map((proof) => {
            const result = results[proof.id];
            const isLoading = loading[proof.id];
            const Icon = proof.icon;

            return (
              <Card key={proof.id} className={result?.success ? "border-green-500/50" : ""}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Icon className={`h-6 w-6 ${proof.color}`} />
                      <CardTitle className="text-lg">{proof.name}</CardTitle>
                    </div>
                    {result && (
                      result.success ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500" />
                      )
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">{proof.description}</p>
                </CardHeader>
                
                <CardContent>
                  {result && (
                    <div className="mb-4 space-y-2">
                      <div className="text-xs text-muted-foreground">
                        Executed: {new Date(result.executed_at).toLocaleString()}
                      </div>
                      
                      <ScrollArea className="h-32 rounded border bg-muted/50 p-2">
                        <div className="space-y-1 font-mono text-xs">
                          {result.logs.map((log, i) => (
                            <div key={i} className="text-muted-foreground">
                              {log}
                            </div>
                          ))}
                        </div>
                      </ScrollArea>

                      <div className="text-xs">
                        <span className="font-medium">Evidence:</span>
                        <pre className="mt-1 rounded bg-muted p-2 overflow-auto text-[10px]">
                          {JSON.stringify(result.evidence, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}

                  <Button 
                    onClick={() => runProof(proof.id)}
                    disabled={isLoading || runningAll}
                    className="w-full"
                    variant={result?.success ? "outline" : "default"}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Executing...
                      </>
                    ) : result ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Re-run
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Execute Proof
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Proof History */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Proof Execution History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No proofs executed yet. Run proofs above to generate evidence.
              </p>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <div 
                    key={item.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                  >
                    <div className="flex items-center gap-3">
                      {item.event_data.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                      <div>
                        <div className="font-medium text-sm">
                          {item.event_data.proof_type.replace(/_/g, " ").replace("proof ", "")}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(item.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <Badge variant={item.event_data.success ? "default" : "destructive"}>
                      {item.event_data.success ? "PASSED" : "FAILED"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
