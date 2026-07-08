"""
LEO AI V42 - The Irrelevance Engine
Phase 3: Mamba O(n) + Speculative Decoding Stack

WebSocket streaming endpoint for speculative decoding.
Streams generated tokens to the frontend while simultaneously
reporting speculative acceptance rates and latency metrics.
"""

import time
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/v1/inference/stream")
async def inference_stream(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            req = json.loads(data)
            
            prompt = req.get("prompt", "")
            max_tokens = req.get("max_tokens", 128)
            speculative_mode = req.get("speculative_mode", "PEARL")
            
            # Send initial acknowledgement
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": f"Starting generation for prompt: {prompt[:20]}..."
            }))
            
            generated_tokens = 0
            total_drafted = 0
            total_accepted = 0
            start_time = time.time()
            
            # Simulate streaming generation loop
            while generated_tokens < max_tokens:
                step_start = time.time()
                
                # 1. Draft phase (simulate PEARL drafting 4 tokens)
                gamma = 4
                total_drafted += gamma
                
                # Simulate draft latency (very fast since we use early layers / tiny model)
                await asyncio.sleep(0.01) 
                
                # 2. Verify phase (simulate batch verification taking a bit longer)
                await asyncio.sleep(0.04)
                
                # Simulate acceptance rate based on mode
                if speculative_mode == "PEARL":
                    accepted = min(gamma, 3) # typically high acceptance for PEARL
                elif speculative_mode == "EAGLE-3":
                    accepted = min(gamma, 2)
                else:
                    accepted = 1 # standard autoregressive (1 by 1)
                    gamma = 1
                    
                total_accepted += accepted
                
                # Output accepted tokens
                for _ in range(accepted):
                    if generated_tokens >= max_tokens:
                        break
                    
                    generated_tokens += 1
                    
                    # Mock token string
                    token_str = f" t{generated_tokens}"
                    
                    step_latency = (time.time() - step_start) * 1000 / accepted
                    current_tps = generated_tokens / (time.time() - start_time)
                    acc_rate = total_accepted / total_drafted if total_drafted > 0 else 1.0
                    
                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "text": token_str,
                        "metrics": {
                            "tokens_per_sec": round(current_tps, 2),
                            "acceptance_rate": round(acc_rate * 100, 1),
                            "latency_per_token_ms": round(step_latency, 2)
                        }
                    }))
                    
            await websocket.send_text(json.dumps({
                "type": "done",
                "message": "Generation complete."
            }))
            
    except WebSocketDisconnect:
        print("Client disconnected from inference stream.")
    except Exception as e:
        print(f"Error in inference stream: {e}")
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except:
            pass
