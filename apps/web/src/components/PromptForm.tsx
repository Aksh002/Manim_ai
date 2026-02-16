"use client";

import { FormEvent, useState } from "react";
import { DifficultyLevel, GeneratePayload, StylePreset } from "@/lib/types";

type Props = {
  loading: boolean;
  onSubmit: (payload: GeneratePayload) => Promise<void>;
};

export default function PromptForm({ loading, onSubmit }: Props) {
  const [topic, setTopic] = useState("Explain the Pythagorean theorem visually");
  const [durationSeconds, setDurationSeconds] = useState(60);
  const [style, setStyle] = useState<StylePreset>("geometric-heavy");
  const [level, setLevel] = useState<DifficultyLevel>("school");
  const [additionalInstructions, setAdditionalInstructions] = useState("Use area transformations.");

  async function submitForm(event: FormEvent) {
    event.preventDefault();
    await onSubmit({
      topic,
      duration_seconds: durationSeconds,
      style,
      level,
      additional_instructions: additionalInstructions
    });
  }

  return (
    <form className="card" onSubmit={submitForm}>
      <h2>Prompt Input</h2>

      <label htmlFor="topic">Topic</label>
      <input id="topic" value={topic} onChange={(e) => setTopic(e.target.value)} required />

      <div className="row" style={{ marginTop: 10 }}>
        <div>
          <label htmlFor="duration">Duration (seconds)</label>
          <input
            id="duration"
            type="number"
            min={15}
            max={180}
            value={durationSeconds}
            onChange={(e) => setDurationSeconds(Number(e.target.value))}
          />
        </div>

        <div>
          <label htmlFor="style">Style</label>
          <select id="style" value={style} onChange={(e) => setStyle(e.target.value as StylePreset)}>
            <option value="minimal">Minimal</option>
            <option value="colorful">Colorful</option>
            <option value="geometric-heavy">Geometric-heavy</option>
          </select>
        </div>
      </div>

      <div className="row" style={{ marginTop: 10 }}>
        <div>
          <label htmlFor="level">Level</label>
          <select id="level" value={level} onChange={(e) => setLevel(e.target.value as DifficultyLevel)}>
            <option value="school">School</option>
            <option value="undergraduate">Undergraduate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div>
          <label htmlFor="instructions">Additional Instructions</label>
          <input
            id="instructions"
            value={additionalInstructions}
            onChange={(e) => setAdditionalInstructions(e.target.value)}
          />
        </div>
      </div>

      <div className="actions">
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Code"}
        </button>
      </div>
    </form>
  );
}
