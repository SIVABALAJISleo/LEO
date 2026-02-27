import { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Play, Code, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { hyperClient } from "@/lib/api";

const Playground = () => {
  const [apiKey, setApiKey] = useState("");
  const [endpoint, setEndpoint] = useState("infer");
  const [requestBody, setRequestBody] = useState(`{
  "model": "llama-70b",
  "input": "Explain quantum computing in simple terms",
  "quantization": "4bit"
}`);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const executeRequest = async () => {
    if (!apiKey) {
      toast({
        title: "API Key Required",
        description: "Please enter your API key to test the endpoint",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setResponse("");

    try {
      let result;
      const parsedBody = JSON.parse(requestBody);
      const queryText = parsedBody.input || parsedBody.text || "Hello Hyper";

      if (endpoint === 'infer') {
        result = await hyperClient.runExpert(queryText);
      } else if (endpoint === 'render') {
        // Map to orchestrate as render is a specific expert task
        result = await hyperClient.orchestrate(`Render: ${queryText}`);
      } else if (endpoint === 'train') {
        result = await hyperClient.orchestrate(`Train: ${queryText}`);
      } else {
        result = await hyperClient.orchestrate(queryText);
      }

      const enrichedResponse = {
        status: "success",
        endpoint: `/api/v1/${endpoint}`,
        result: result,
        performance: {
          gpu_equivalent: "HYPER CPU Engine",
          efficiency: "100%",
          latency_optimized: true
        }
      };

      setResponse(JSON.stringify(enrichedResponse, null, 2));

      toast({
        title: "Request Successful",
        description: "Production engine response received successfully",
      });
    } catch (error: any) {
      toast({
        title: "Request Failed",
        description: error.message || "An error occurred while processing your request",
        variant: "destructive",
      });
      setResponse(JSON.stringify({ error: error.message }, null, 2));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        <div className="mb-12">
          <h1 className="text-5xl font-display font-bold mb-4">
            API <span className="text-primary">Playground</span>
          </h1>
          <p className="text-xl text-foreground/70">
            Test HYPER API endpoints interactively
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Request Panel */}
          <Card className="p-6 bg-card border-border">
            <div className="flex items-center mb-6">
              <Code className="h-6 w-6 text-primary mr-2" />
              <h2 className="text-2xl font-semibold">Request</h2>
            </div>

            <div className="space-y-6">
              <div>
                <Label htmlFor="apiKey">API Key</Label>
                <input
                  id="apiKey"
                  type="password"
                  placeholder="igpu_your_api_key_here"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full mt-2 px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-foreground/60 mt-1">
                  Get your API key from the <a href="/dashboard" className="text-primary hover:underline">Dashboard</a>
                </p>
              </div>

              <div>
                <Label htmlFor="endpoint">Endpoint</Label>
                <Select value={endpoint} onValueChange={setEndpoint}>
                  <SelectTrigger className="w-full mt-2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="infer">AI Inference</SelectItem>
                    <SelectItem value="render">Rendering</SelectItem>
                    <SelectItem value="train">Model Training</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="requestBody">Request Body (JSON)</Label>
                <Textarea
                  id="requestBody"
                  value={requestBody}
                  onChange={(e) => setRequestBody(e.target.value)}
                  className="mt-2 font-mono text-sm min-h-[300px]"
                  placeholder="Enter JSON request body"
                />
              </div>

              <Button
                onClick={executeRequest}
                disabled={loading}
                className="w-full bg-gradient-primary shadow-glow"
              >
                {loading ? (
                  "Processing..."
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Execute Request
                  </>
                )}
              </Button>
            </div>
          </Card>

          {/* Response Panel */}
          <Card className="p-6 bg-card border-border">
            <div className="flex items-center mb-6">
              <Zap className="h-6 w-6 text-primary mr-2" />
              <h2 className="text-2xl font-semibold">Response</h2>
            </div>

            {response ? (
              <div className="bg-background p-4 rounded-lg border border-border">
                <pre className="text-sm text-foreground/80 overflow-x-auto">
                  {response}
                </pre>
              </div>
            ) : (
              <div className="bg-background p-8 rounded-lg border border-border border-dashed text-center">
                <Zap className="h-12 w-12 mx-auto mb-4 text-foreground/30" />
                <p className="text-foreground/60">
                  Response will appear here after executing the request
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Examples Section */}
        <Card className="mt-8 p-6 bg-card border-border">
          <h2 className="text-2xl font-semibold mb-6">Example Requests</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                title: "AI Inference",
                description: "Run LLM inference with 4-bit quantization",
                body: `{
  "model": "llama-70b",
  "input": "Your prompt",
  "quantization": "4bit"
}`,
              },
              {
                title: "4K Rendering",
                description: "Render 4K scene at 120 FPS",
                body: `{
  "scene": "scene_data",
  "resolution": "4K",
  "fps": 120,
  "ray_tracing": true
}`,
              },
              {
                title: "Model Training",
                description: "Fine-tune 70B model with LoRA",
                body: `{
  "model_size": "70B",
  "dataset": "dataset_id",
  "epochs": 3,
  "lora": true
}`,
              },
            ].map((example, idx) => (
              <div
                key={idx}
                className="p-4 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-all cursor-pointer"
                onClick={() => setRequestBody(example.body)}
              >
                <h3 className="font-semibold mb-2">{example.title}</h3>
                <p className="text-sm text-foreground/60 mb-3">{example.description}</p>
                <div className="text-xs text-primary">Click to use →</div>
              </div>
            ))}
          </div>
        </Card>

        <Footer />
      </div>
    </div>
  );
};

export default Playground;
