import React, { useState } from "react";
import { Code, Zap, Play } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { hyperClient } from "../lib/api";
import { useToast } from "../hooks/use-toast";

export const IntelliGPUPlayground = () => {
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
      const queryText = parsedBody.input || parsedBody.question || parsedBody.text || "Hello Hyper";

      result = await hyperClient.runExpert(queryText);
      setResponse(JSON.stringify(result, null, 2));

      toast({
        title: "Request Successful",
        description: `Source: ${result.source || "Local Engine"} | Latency: ${result.latency_ms || 20}ms`,
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
    <div className="bg-[#020813] text-slate-100 min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12 text-center md:text-left">
          <h1 className="text-4xl font-extrabold text-white font-display mb-3 tracking-tight">
            API <span className="text-[#76B900]">Playground</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base max-w-3xl">
            Test IntelliGPU API endpoints interactively
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Request Panel */}
          <Card className="bg-[#030c1b] border border-slate-800/80">
            <CardContent className="p-6">
              <div className="flex items-center mb-6">
                <Code className="h-6 w-6 text-[#76B900] mr-2" />
                <h2 className="text-xl font-bold text-white">Request</h2>
              </div>

              <div className="space-y-6">
                <div>
                  <Label htmlFor="apiKey" className="text-slate-300 font-bold text-xs uppercase">
                    API Key
                  </Label>
                  <input
                    id="apiKey"
                    type="password"
                    placeholder="igpu_your_api_key_here"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="w-full mt-2 px-4 py-2 bg-[#020813] border border-slate-800 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#76B900] text-xs font-mono"
                  />
                  <p className="text-[10px] text-slate-500 mt-1">
                    Enter any text (e.g. `igpu_demo_key`) to activate local sandbox runs.
                  </p>
                </div>

                <div>
                  <Label htmlFor="endpoint" className="text-slate-300 font-bold text-xs uppercase">
                    Endpoint
                  </Label>
                  <Select value={endpoint} onValueChange={setEndpoint}>
                    <SelectTrigger className="w-full mt-2 bg-[#020813] border-slate-800 text-slate-300 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#030c1b] border-slate-800 text-slate-300">
                      <SelectItem value="infer" className="text-xs">
                        AI Inference
                      </SelectItem>
                      <SelectItem value="render" className="text-xs">
                        Rendering
                      </SelectItem>
                      <SelectItem value="train" className="text-xs">
                        Model Training
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label
                    htmlFor="requestBody"
                    className="text-slate-300 font-bold text-xs uppercase"
                  >
                    Request Body (JSON)
                  </Label>
                  <Textarea
                    id="requestBody"
                    value={requestBody}
                    onChange={(e) => setRequestBody(e.target.value)}
                    className="mt-2 font-mono text-xs min-h-[220px] bg-[#020813] border-slate-800 text-slate-300"
                    placeholder="Enter JSON request body"
                  />
                </div>

                <Button
                  onClick={executeRequest}
                  disabled={loading}
                  className="w-full bg-[#76B900] hover:bg-[#659e00] text-black font-extrabold text-xs py-5 rounded shadow-[0_0_15px_rgba(118,185,0,0.3)]"
                >
                  {loading ? (
                    "Processing..."
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4 fill-current" />
                      Execute Request
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Response Panel */}
          <Card className="bg-[#030c1b] border border-slate-800/80">
            <CardContent className="p-6">
              <div className="flex items-center mb-6">
                <Zap className="h-6 w-6 text-[#76B900] mr-2" />
                <h2 className="text-xl font-bold text-white">Response</h2>
              </div>

              {response ? (
                <div className="bg-[#020813] p-4 rounded-lg border border-slate-800">
                  <pre className="text-xs font-mono text-slate-300 overflow-x-auto whitespace-pre">
                    {response}
                  </pre>
                </div>
              ) : (
                <div className="bg-[#020813] p-12 rounded-lg border border-slate-800 border-dashed text-center">
                  <Zap className="h-10 w-10 mx-auto mb-4 text-slate-700" />
                  <p className="text-slate-500 text-xs">
                    Response will appear here after executing the request
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Examples Section */}
        <Card className="mt-8 bg-[#030c1b] border border-slate-800/80">
          <CardContent className="p-6">
            <h2 className="text-lg font-bold text-white mb-6">Example Requests</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                {
                  title: "AI Inference",
                  description: "Run LLM inference with 4-bit quantization",
                  body: `{
  "model": "llama-70b",
  "input": "Explain quantum computing in simple terms",
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
                  className="p-4 bg-[#020813] rounded-lg border border-slate-800 hover:border-[#76B900]/50 transition-all cursor-pointer group"
                  onClick={() => setRequestBody(example.body)}
                >
                  <h3 className="font-bold text-slate-200 mb-1 text-xs">{example.title}</h3>
                  <p className="text-[11px] text-slate-500 mb-3 leading-relaxed">
                    {example.description}
                  </p>
                  <div className="text-[10px] text-[#76B900] font-bold group-hover:translate-x-1 transition-transform">
                    Click to use →
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
