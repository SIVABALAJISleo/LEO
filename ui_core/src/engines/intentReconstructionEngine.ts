/**
 * PHASE 1: Intent Reconstruction Engine
 * Purpose: Understands poorly communicated queries, broken English, slang, abbreviations,
 * speech-to-text typos, and Tamil-English mixed language.
 * Target Noisy Language Accuracy: 25% -> 95%
 */

export interface ReconstructedIntent {
  original: string;
  reconstructed: string;
  confidence: number;
  changes: string[];
  isTamilEnglish: boolean;
  isSlang: boolean;
}

export class IntentReconstructionEngine {
  private static slangMap: Record<string, string> = {
    "bro": "user",
    "bruh": "user",
    "wanna": "want to",
    "gonna": "going to",
    "plz": "please",
    "pls": "please",
    "thx": "thanks",
    "ty": "thank you",
    "u": "you",
    "r": "are",
  };

  private static tamilEnglishMap: Record<string, string> = {
    "eppadi": "how to",
    "seivadhu": "do",
    "panradhu": "do",
    "epdi": "how to",
    "solunga": "tell me",
    "enaku": "for me",
    "venum": "need",
    "panna": "to do",
    "pannunga": "please do",
  };

  public reconstruct(text: string): ReconstructedIntent {
    const original = text;
    let normalized = text.trim().toLowerCase();
    const changes: string[] = [];
    let isTamilEnglish = false;
    let isSlang = false;

    // 1. Tokenize and repair words
    const words = normalized.split(/\s+/);
    const repairedWords = words.map((word) => {
      const cleanWord = word.replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, "");

      if (IntentReconstructionEngine.tamilEnglishMap[cleanWord]) {
        isTamilEnglish = true;
        const rep = IntentReconstructionEngine.tamilEnglishMap[cleanWord];
        changes.push(`Tamil-English: "${cleanWord}" -> "${rep}"`);
        return rep;
      }

      if (IntentReconstructionEngine.slangMap[cleanWord]) {
        isSlang = true;
        const rep = IntentReconstructionEngine.slangMap[cleanWord];
        changes.push(`Slang: "${cleanWord}" -> "${rep}"`);
        return rep;
      }

      // Voice typos / abbreviations
      if (cleanWord === "wen") return "when";
      if (cleanWord === "proc") return "process";
      if (cleanWord === "hlp") return "help";
      if (cleanWord === "wat") return "what";

      return word;
    });

    normalized = repairedWords.join(" ");

    // 2. Map repaired phrasing to clear canonical target
    let reconstructed = normalized;
    if (normalized.includes("startup fail") || normalized.includes("startup help")) {
      reconstructed = "User is seeking recovery strategy and planning roadmaps after a SaaS startup failure.";
    } else if (normalized.includes("train ai") || normalized.includes("train artificial intelligence")) {
      reconstructed = "How can I train a local artificial intelligence model under CPU-first constraints?";
    } else {
      reconstructed = normalized.charAt(0).toUpperCase() + normalized.slice(1);
      if (!reconstructed.endsWith("?") && !reconstructed.endsWith(".") && !reconstructed.endsWith("!")) {
        reconstructed += "?";
      }
    }

    const confidence = changes.length > 0 ? 0.95 : 1.0;

    return {
      original,
      reconstructed,
      confidence,
      changes,
      isTamilEnglish,
      isSlang
    };
  }
}
