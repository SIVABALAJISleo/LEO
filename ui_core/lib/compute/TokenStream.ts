export class TokenStream {
  // Simulate streaming text output
  static async *stream(text: string, delayMs: number = 20): AsyncGenerator<string> {
    const tokens = text.split(/(?=[ {.,}])/); // simple tokenization split by word/punctuation

    for (const token of tokens) {
      await new Promise((r) => setTimeout(r, delayMs)); // Simulate inference time
      yield token;
    }
  }
}
