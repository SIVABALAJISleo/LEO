// V22 — Phase 4: Language Recovery Engine V2
// Handles Broken English, Tamil-English, slang, typos, ambiguous / incomplete queries

export type LanguageIssue =
  "broken_english" | "tanglish" | "slang" | "typo" | "incomplete" | "ambiguous" | "code_switch";

export interface RecoveryRepair {
  original: string;
  repaired: string;
  issueType: LanguageIssue;
  confidence: number;
}

export interface LanguageRecoveryV2Result {
  rawInput: string;
  detectedIssues: LanguageIssue[];
  repairs: RecoveryRepair[];
  reconstructedQuery: string;
  intentConfidence: number;
  clarifyingQuestion?: string;
  languageProfile: {
    isTanglish: boolean;
    hasSlang: boolean;
    hasTypos: boolean;
    isIncomplete: boolean;
    isAmbiguous: boolean;
  };
}

// Tamil-English (Tanglish) vocabulary map
const TANGLISH_MAP: Record<string, string> = {
  eppadi: "how to",
  panradhu: "do",
  iruku: "is / are",
  sollu: "tell",
  theriyum: "I know",
  theriyathu: "I don't know",
  romba: "very",
  nalla: "good",
  konjam: "little",
  poi: "go",
  va: "come",
  da: "",
  di: "",
  bro: "friend",
  machaan: "friend",
  yenna: "what",
  yaar: "who",
  eppo: "when",
  enga: "where",
};

// Slang map
const SLANG_MAP: Record<string, string> = {
  wat: "what",
  wut: "what",
  cuz: "because",
  gonna: "going to",
  wanna: "want to",
  gotta: "have to",
  kinda: "kind of",
  lemme: "let me",
  gimme: "give me",
  dunno: "don't know",
  tbh: "to be honest",
  rn: "right now",
  asap: "as soon as possible",
  imo: "in my opinion",
  idk: "I don't know",
  ngl: "not going to lie",
  lmk: "let me know",
  fyi: "for your information",
  smth: "something",
};

// Common typo corrections
const TYPO_MAP: Record<string, string> = {
  teh: "the",
  recieve: "receive",
  definately: "definitely",
  occured: "occurred",
  seperate: "separate",
  untill: "until",
  begining: "beginning",
  grammer: "grammar",
  adress: "address",
  occurance: "occurrence",
};

export class LanguageRecoveryEngineV2 {
  private totalProcessed = 0;
  private totalIntentScore = 0;

  recover(rawInput: string): LanguageRecoveryV2Result {
    this.totalProcessed++;
    const lower = rawInput.toLowerCase();
    const words = rawInput.split(/\s+/);

    const detectedIssues: LanguageIssue[] = [];
    const repairs: RecoveryRepair[] = [];
    const repairedWords = [...words];

    // --- Tanglish detection & repair ---
    let hasTanglish = false;
    words.forEach((word, idx) => {
      const lw = word.toLowerCase().replace(/[^a-z]/g, "");
      if (TANGLISH_MAP[lw] !== undefined) {
        hasTanglish = true;
        const replacement = TANGLISH_MAP[lw];
        repairs.push({
          original: word,
          repaired: replacement,
          issueType: "tanglish",
          confidence: 0.93,
        });
        repairedWords[idx] = replacement;
      }
    });
    if (hasTanglish) detectedIssues.push("tanglish");

    // --- Slang detection & repair ---
    let hasSlang = false;
    repairedWords.forEach((word, idx) => {
      const lw = word.toLowerCase().replace(/[^a-z]/g, "");
      if (SLANG_MAP[lw]) {
        hasSlang = true;
        repairs.push({
          original: word,
          repaired: SLANG_MAP[lw],
          issueType: "slang",
          confidence: 0.96,
        });
        repairedWords[idx] = SLANG_MAP[lw];
      }
    });
    if (hasSlang) detectedIssues.push("slang");

    // --- Typo detection & repair ---
    let hasTypos = false;
    repairedWords.forEach((word, idx) => {
      const lw = word.toLowerCase().replace(/[^a-z]/g, "");
      if (TYPO_MAP[lw]) {
        hasTypos = true;
        repairs.push({
          original: word,
          repaired: TYPO_MAP[lw],
          issueType: "typo",
          confidence: 0.98,
        });
        repairedWords[idx] = TYPO_MAP[lw];
      }
    });
    if (hasTypos) detectedIssues.push("typo");

    // --- Broken English detection (very short / missing verbs) ---
    const isBrokenEnglish =
      words.length < 4 && !/\b(is|are|do|does|how|what|why|can|will)\b/i.test(lower);
    if (isBrokenEnglish) {
      detectedIssues.push("broken_english");
      repairs.push({
        original: rawInput,
        repaired: `Please explain: ${rawInput}`,
        issueType: "broken_english",
        confidence: 0.82,
      });
    }

    // --- Incomplete detection ---
    const isIncomplete = rawInput.trim().endsWith("?") === false && words.length < 5;
    if (isIncomplete) detectedIssues.push("incomplete");

    // --- Ambiguity detection ---
    const ambiguousTerms = ["it", "this", "that", "thing", "stuff", "them"];
    const isAmbiguous = ambiguousTerms.some(
      (t) => lower.includes(` ${t} `) || lower.startsWith(`${t} `),
    );
    if (isAmbiguous) detectedIssues.push("ambiguous");

    // Build reconstructed query
    let reconstructed = repairedWords
      .filter(Boolean)
      .join(" ")
      .replace(/\s{2,}/g, " ")
      .trim();
    if (isBrokenEnglish && !reconstructed.toLowerCase().startsWith("please")) {
      reconstructed = `Please explain: ${reconstructed}`;
    }

    // Clarifying question for ambiguous/incomplete
    let clarifyingQuestion: string | undefined;
    if (isAmbiguous || isIncomplete) {
      clarifyingQuestion = `To give you the best answer, could you clarify: What specific aspect of "${reconstructed.slice(0, 50)}" are you asking about?`;
    }

    // Intent confidence
    const baseConf = 0.88;
    const issuesPenalty = detectedIssues.length * 0.015;
    const repairBonus = repairs.length * 0.01;
    const intentConfidence = Math.min(0.99, Math.max(0.72, baseConf - issuesPenalty + repairBonus));
    this.totalIntentScore += intentConfidence;

    return {
      rawInput,
      detectedIssues,
      repairs,
      reconstructedQuery: reconstructed,
      intentConfidence,
      clarifyingQuestion,
      languageProfile: {
        isTanglish: hasTanglish,
        hasSlang,
        hasTypos,
        isIncomplete,
        isAmbiguous,
      },
    };
  }

  getStats() {
    return {
      totalProcessed: this.totalProcessed,
      averageIntentAccuracy:
        this.totalProcessed > 0 ? this.totalIntentScore / this.totalProcessed : 0,
    };
  }
}
