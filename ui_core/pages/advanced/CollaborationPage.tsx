import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Users, MessageSquare, Lock, History, ThumbsUp, Plus, Copy, Send } from "lucide-react";
import { useCollaborationData } from "@/hooks/useCollaborationData";
import { LoadingState } from "@/components/ui/loading-state";
import { EmptyState } from "@/components/ui/empty-state";

const CollaborationPage = () => {
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [newSessionName, setNewSessionName] = useState("");
  const [joinRoomId, setJoinRoomId] = useState("");
  const [messageInput, setMessageInput] = useState("");

  const {
    sessions,
    currentSession,
    participants,
    messages,
    changes,
    locks,
    isLoading,
    createSession,
    joinSession,
    sendMessage,
  } = useCollaborationData(sessionId);

  const handleCreateSession = async () => {
    if (!newSessionName.trim()) return;
    const session = await createSession(newSessionName);
    if (session) {
      setSessionId(session.id);
      setNewSessionName("");
    }
  };

  const handleJoinSession = async () => {
    if (!joinRoomId.trim()) return;
    const session = await joinSession(joinRoomId);
    if (session) {
      setSessionId(session.id);
      setJoinRoomId("");
    }
  };

  const handleSendMessage = async () => {
    if (!messageInput.trim()) return;
    await sendMessage(messageInput);
    setMessageInput("");
  };

  if (isLoading) return <LoadingState message="Loading collaboration..." />;

  if (!sessionId) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Real-Time Collaboration</h1>
            <p className="text-muted-foreground">Collaborate on inference jobs with your team</p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Create New Session</CardTitle>
              <CardDescription>Start a new collaborative workspace</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Session name"
                value={newSessionName}
                onChange={(e) => setNewSessionName(e.target.value)}
              />
              <Button onClick={handleCreateSession} className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Create Session
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Join Session</CardTitle>
              <CardDescription>Enter a room ID to join</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Room ID"
                value={joinRoomId}
                onChange={(e) => setJoinRoomId(e.target.value)}
              />
              <Button onClick={handleJoinSession} variant="secondary" className="w-full">
                <Users className="mr-2 h-4 w-4" />
                Join Session
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Your Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            {sessions.length === 0 ? (
              <EmptyState
                title="No sessions"
                description="Create or join a session to get started"
              />
            ) : (
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{session.name}</p>
                      <p className="text-sm text-muted-foreground">Room: {session.room_id}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigator.clipboard.writeText(session.room_id)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button size="sm" onClick={() => setSessionId(session.id)}>
                        Open
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{currentSession?.name || "Collaboration Session"}</h1>
          <p className="text-sm text-muted-foreground">Room: {currentSession?.room_id}</p>
        </div>
        <Button variant="outline" onClick={() => setSessionId(undefined)}>
          Leave Session
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4 flex-1">
        <Card className="md:col-span-3">
          <Tabs defaultValue="modules" className="h-full">
            <CardHeader className="pb-2">
              <TabsList>
                <TabsTrigger value="modules">Modules</TabsTrigger>
                <TabsTrigger value="history">History</TabsTrigger>
                <TabsTrigger value="votes">Votes</TabsTrigger>
              </TabsList>
            </CardHeader>
            <CardContent>
              <TabsContent value="modules" className="mt-0">
                <div className="grid gap-3 md:grid-cols-3">
                  {[
                    "Quantization",
                    "Kernel Optimization",
                    "Memory Compression",
                    "Cache Optimization",
                    "Parallel Execution",
                  ].map((module) => {
                    const lock = locks.find((l) => l.module_name === module);
                    return (
                      <Card key={module} className={lock ? "border-yellow-500" : ""}>
                        <CardHeader className="p-3">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-sm">{module}</CardTitle>
                            {lock && <Lock className="h-4 w-4 text-yellow-500" />}
                          </div>
                        </CardHeader>
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>
              <TabsContent value="history" className="mt-0">
                <ScrollArea className="h-64">
                  {changes.length === 0 ? (
                    <EmptyState title="No changes yet" />
                  ) : (
                    changes.map((change) => (
                      <div key={change.id} className="flex items-center gap-2 p-2 border-b">
                        <History className="h-4 w-4" />
                        <span className="text-sm">
                          {change.change_type} on {change.target_module}
                        </span>
                        <Badge variant="outline">
                          {new Date(change.created_at).toLocaleTimeString()}
                        </Badge>
                      </div>
                    ))
                  )}
                </ScrollArea>
              </TabsContent>
              <TabsContent value="votes" className="mt-0">
                <div className="flex items-center gap-4 p-4">
                  <Button>
                    <ThumbsUp className="mr-2 h-4 w-4" />
                    Approve Configuration
                  </Button>
                </div>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Users className="h-4 w-4" />
                Participants ({participants.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {participants.map((p) => (
                <div key={p.id} className="flex items-center gap-2 py-1">
                  <div
                    className={`w-2 h-2 rounded-full ${p.is_online ? "bg-green-500" : "bg-gray-400"}`}
                  />
                  <span className="text-sm">{p.user_id.slice(0, 8)}</span>
                  <Badge variant="outline" className="text-xs">
                    {p.role}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="flex-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Chat
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-32 mb-2">
                {messages.map((msg) => (
                  <div key={msg.id} className="text-sm py-1">
                    <span className="font-medium">{msg.user_id.slice(0, 6)}:</span> {msg.content}
                  </div>
                ))}
              </ScrollArea>
              <div className="flex gap-2">
                <Input
                  placeholder="Message..."
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                />
                <Button size="icon" onClick={handleSendMessage}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CollaborationPage;
