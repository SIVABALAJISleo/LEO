export type StreamEvent = {
    type: 'chunk' | 'metadata' | 'done' | 'error';
    content?: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    data?: any;
};

export class StreamingInference {
    /**
     * Simulates a streaming AI response by yielding chunks of text.
     * In a production environment, this would process a ReadableStream from a fetch call.
     */
    static async *streamResponse(fullText: string, chunkMs: number = 50): AsyncGenerator<StreamEvent> {
        try {
            // Initial metadata event
            yield { type: 'metadata', data: { startedAt: Date.now(), model: 'hyper-tiny-v1' } };

            const words = fullText.split(' ');
            for (let i = 0; i < words.length; i++) {
                // Return a chunk of words to simulate realistic streaming speed
                const chunk = words[i] + (i === words.length - 1 ? '' : ' ');
                yield { type: 'chunk', content: chunk };

                // Simulate periodic latency
                if (i % 5 === 0) {
                    await new Promise(r => setTimeout(r, chunkMs * 2));
                } else {
                    await new Promise(r => setTimeout(r, chunkMs));
                }
            }

            yield { type: 'done', data: { finishedAt: Date.now(), tokens: words.length } };
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: any) {
            yield { type: 'error', content: error.message || 'Streaming failed' };
        }
    }
}
