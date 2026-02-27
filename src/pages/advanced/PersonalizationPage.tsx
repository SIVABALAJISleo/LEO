import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { User, Settings, Sparkles, LayoutGrid, Moon, Sun, Monitor } from 'lucide-react';
import { usePersonalizationData } from '@/hooks/usePersonalizationData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';

const PersonalizationPage = () => {
  const { settings, behaviors, recommendations, isLoading, updateSettings } = usePersonalizationData();

  const handleThemeChange = async (theme: string) => {
    await updateSettings({ theme_preference: theme });
  };

  const handleLayoutChange = async (layout: string) => {
    await updateSettings({ layout_preference: layout });
  };

  const handleNotificationToggle = async (key: string, value: boolean) => {
    const currentPrefs = (settings?.notification_preferences as Record<string, boolean>) || {};
    await updateSettings({ notification_preferences: { ...currentPrefs, [key]: value } });
  };

  if (isLoading) return <LoadingState message="Loading personalization..." />;

  const notificationPrefs = (settings?.notification_preferences as Record<string, boolean>) || {};
  const featureFlags = (settings?.feature_flags as Record<string, boolean>) || {};

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Personalization</h1>
        <p className="text-muted-foreground">Customize your experience with behavioral tracking and recommendations</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Behaviors Tracked</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{behaviors.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Recommendations</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{recommendations.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Theme</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold capitalize">{settings?.theme_preference || 'system'}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Layout</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold capitalize">{settings?.layout_preference || 'default'}</p></CardContent>
        </Card>
      </div>

      <Tabs defaultValue="preferences">
        <TabsList>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="behaviors">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="preferences" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Settings className="h-5 w-5" /> Appearance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Theme</Label>
                  <p className="text-sm text-muted-foreground">Choose your preferred color scheme</p>
                </div>
                <div className="flex gap-2">
                  <Button variant={settings?.theme_preference === 'light' ? 'default' : 'outline'} size="sm" onClick={() => handleThemeChange('light')}>
                    <Sun className="h-4 w-4 mr-1" /> Light
                  </Button>
                  <Button variant={settings?.theme_preference === 'dark' ? 'default' : 'outline'} size="sm" onClick={() => handleThemeChange('dark')}>
                    <Moon className="h-4 w-4 mr-1" /> Dark
                  </Button>
                  <Button variant={settings?.theme_preference === 'system' ? 'default' : 'outline'} size="sm" onClick={() => handleThemeChange('system')}>
                    <Monitor className="h-4 w-4 mr-1" /> System
                  </Button>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Layout</Label>
                  <p className="text-sm text-muted-foreground">Choose your dashboard layout</p>
                </div>
                <Select value={settings?.layout_preference || 'default'} onValueChange={handleLayoutChange}>
                  <SelectTrigger className="w-40"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Default</SelectItem>
                    <SelectItem value="compact">Compact</SelectItem>
                    <SelectItem value="expanded">Expanded</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Sparkles className="h-5 w-5" /> Notifications</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {['email', 'push', 'job_complete', 'alerts', 'weekly_digest'].map((key) => (
                <div key={key} className="flex items-center justify-between">
                  <Label className="capitalize">{key.replace('_', ' ')}</Label>
                  <Switch checked={notificationPrefs[key] ?? true} onCheckedChange={(v) => handleNotificationToggle(key, v)} />
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><LayoutGrid className="h-5 w-5" /> Feature Flags</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(featureFlags).length === 0 ? (
                <p className="text-muted-foreground">No feature flags configured</p>
              ) : (
                Object.entries(featureFlags).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <Label className="capitalize">{key.replace('_', ' ')}</Label>
                    <Badge variant={value ? 'default' : 'secondary'}>{value ? 'Enabled' : 'Disabled'}</Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          {recommendations.length === 0 ? (
            <EmptyState title="No recommendations yet" description="Use the platform more to receive personalized recommendations" icon={Sparkles} />
          ) : (
            <div className="space-y-2">
              {recommendations.map((r) => (
                <Card key={r.id}>
                  <CardContent className="flex justify-between items-center py-4">
                    <div className="flex items-center gap-4">
                      <Sparkles className="h-8 w-8 text-primary" />
                      <div>
                        <p className="font-medium">{r.recommendation_type}</p>
                        <p className="text-sm text-muted-foreground">Score: {((r.score || 0) * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={r.is_dismissed ? 'secondary' : r.is_applied ? 'default' : 'outline'}>
                        {r.is_dismissed ? 'Dismissed' : r.is_applied ? 'Applied' : 'Pending'}
                      </Badge>
                      {!r.is_dismissed && !r.is_applied && (
                        <Button size="sm">Apply</Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="behaviors" className="space-y-4">
          {behaviors.length === 0 ? (
            <EmptyState title="No activity recorded" description="Your activity will appear here as you use the platform" icon={User} />
          ) : (
            <div className="space-y-2">
              {behaviors.slice(0, 50).map((b) => (
                <Card key={b.id}>
                  <CardContent className="flex justify-between items-center py-3">
                    <div className="flex items-center gap-3">
                      <User className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{b.behavior_type}</p>
                        <p className="text-sm text-muted-foreground">{b.page_path || 'N/A'}</p>
                      </div>
                    </div>
                    <span className="text-sm text-muted-foreground">{new Date(b.created_at).toLocaleString()}</span>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PersonalizationPage;
