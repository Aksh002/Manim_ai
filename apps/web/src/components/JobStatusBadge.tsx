"use client";

type Props = {
  status: string | null;
  progress: number;
  stage: string;
};

export default function JobStatusBadge({ status, progress, stage }: Props) {
  if (!status) {
    return <p>Status: idle</p>;
  }

  return (
    <div>
      <span className={`status ${status}`}>{status}</span>
      <p style={{ marginTop: 8 }}>Stage: {stage} | Progress: {progress}%</p>
    </div>
  );
}
