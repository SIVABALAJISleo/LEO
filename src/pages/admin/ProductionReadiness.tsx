import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, CheckCircle2, XCircle, AlertCircle, Play, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { productionReadinessChecker, type ProductionReadinessScore } from '@/lib/production/ProductionReadinessChecker';
import { launchVerification, type LaunchReadinessReport, type VerificationTest } from '@/lib/production/LaunchVerification';
import { useAdminRole } from '@/hooks/useAdminRole';

const ProductionReadiness = () => {
  const navigate = useNavigate();
  const { isAdmin, isLoading: adminLoading } = useAdminRole();
  const [readiness, setReadiness] = useState<ProductionReadinessScore | null>(null);
  const [verification, setVerification] = useState<LaunchReadinessReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningVerification, setRunningVerification] = useState(false);

  useEffect(() => {
    if (!adminLoading && !isAdmin) {
      navigate('/dashboard');
    }
  }, [isAdmin, adminLoading, navigate]);

  useEffect(() => {
    fetchReadiness();
  }, []);

  const fetchReadiness = async () => {
    setLoading(true);
    try {
      const score = await productionReadinessChecker.getFullReadinessScore();
      setReadiness(score);
    } catch (error) {
      console.error('Failed to fetch readiness:', error);
    } finally {
      setLoading(false);
    }
  };

  const runVerification = async () => {
    setRunningVerification(true);
    try {
      const report = await launchVerification.runFullVerification();
      setVerification(report);
    } catch (error) {
      console.error('Verification failed:', error);
    } finally {
      setRunningVerification(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
      case 'passed':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'partial':
      case 'running':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'missing':
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'production_ready':
      case 'ready':
        return <Badge variant="default" className="bg-green-500">Production Ready</Badge>;
      case 'almost_ready':
      case 'partial':
        return <Badge variant="secondary" className="bg-yellow-500 text-black">Almost Ready</Badge>;
      default:
        return <Badge variant="destructive">Needs Work</Badge>;
    }
  };

  if (adminLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Dashboard
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Production Readiness</h1>
              <p className="text-muted-foreground">System health and launch verification</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchReadiness}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={runVerification} disabled={runningVerification}>
              {runningVerification ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Run Verification
            </Button>
          </div>
        </div>

        {/* Overall Score */}
        {readiness && (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">Overall Readiness</CardTitle>
                  <CardDescription>
                    Last checked: {new Date(readiness.lastChecked).toLocaleString()}
                  </CardDescription>
                </div>
                {getStatusBadge(readiness.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-4">
                <div className="text-5xl font-bold">{readiness.overallPercent}%</div>
                <Progress value={readiness.overallPercent} className="flex-1 h-4" />
              </div>

              {readiness.blockers.length > 0 && (
                <div className="mt-4 p-4 bg-destructive/10 rounded-lg border border-destructive/20">
                  <h4 className="font-semibold text-destructive mb-2">Blockers</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {readiness.blockers.map((blocker, i) => (
                      <li key={i} className="text-sm text-destructive">{blocker}</li>
                    ))}
                  </ul>
                </div>
              )}

              {readiness.deferredItems.length > 0 && (
                <div className="mt-4 p-4 bg-muted rounded-lg">
                  <h4 className="font-semibold text-muted-foreground mb-2">Intentionally Deferred</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {readiness.deferredItems.map((item, i) => (
                      <li key={i} className="text-sm text-muted-foreground">{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="categories">
          <TabsList className="mb-4">
            <TabsTrigger value="categories">Readiness Categories</TabsTrigger>
            <TabsTrigger value="verification">Launch Verification</TabsTrigger>
          </TabsList>

          {/* Categories Tab */}
          <TabsContent value="categories">
            <div className="grid gap-4 md:grid-cols-2">
              {readiness?.categories.map(category => (
                <Card key={category.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{category.name}</CardTitle>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">
                          {category.score}/{category.maxScore}
                        </span>
                        {getStatusIcon(category.status)}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Progress 
                      value={(category.score / category.maxScore) * 100} 
                      className="h-2 mb-4"
                    />
                    <ul className="space-y-2">
                      {category.items.map((item, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm">
                          {item.implemented ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500 shrink-0" />
                          )}
                          <span className={item.critical ? 'font-medium' : ''}>
                            {item.name}
                            {item.critical && (
                              <Badge variant="outline" className="ml-2 text-xs">Critical</Badge>
                            )}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Verification Tab */}
          <TabsContent value="verification">
            {verification ? (
              <div>
                {/* Verification Summary */}
                <Card className="mb-4">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Verification Results</CardTitle>
                      {getStatusBadge(verification.overallStatus)}
                    </div>
                    <CardDescription>
                      {verification.tests.filter(t => t.status === 'passed').length} of {verification.tests.length} tests passed
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress 
                      value={verification.readinessPercent} 
                      className="h-3 mb-4"
                    />

                    {verification.recommendations.length > 0 && (
                      <div className="p-4 bg-muted rounded-lg">
                        <h4 className="font-semibold mb-2">Recommendations</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {verification.recommendations.map((rec, i) => (
                            <li key={i} className="text-sm">{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Test Results by Category */}
                {['auth', 'jobs', 'errors', 'rate_limits', 'backups', 'rollbacks', 'system'].map(category => {
                  const categoryTests = verification.tests.filter(t => t.category === category);
                  if (categoryTests.length === 0) return null;
                  
                  return (
                    <Card key={category} className="mb-4">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg capitalize">{category.replace('_', ' ')} Tests</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {categoryTests.map(test => (
                            <li key={test.id} className="flex items-start gap-2 p-2 rounded bg-muted/50">
                              {getStatusIcon(test.status)}
                              <div className="flex-1">
                                <div className="font-medium">{test.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  {test.result || test.error || test.description}
                                </div>
                                {test.durationMs && (
                                  <div className="text-xs text-muted-foreground mt-1">
                                    Duration: {test.durationMs}ms
                                  </div>
                                )}
                              </div>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-muted-foreground mb-4">
                    No verification results yet. Run the verification to test all systems.
                  </p>
                  <Button onClick={runVerification} disabled={runningVerification}>
                    {runningVerification ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4 mr-2" />
                    )}
                    Run Verification
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ProductionReadiness;
