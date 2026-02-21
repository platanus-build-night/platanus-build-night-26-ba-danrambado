"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { VoiceInput } from "@/components/voice-input";
import { api } from "@/lib/api";

const TYPE_LABELS: Record<string, string> = {
  project: "Project",
  collab: "Collaboration",
  date: "Date",
  help: "Help / Mentoring",
  job: "Job / Work",
  fun: "Fun",
};

interface Experience {
  opportunity_id: string;
  opportunity_type: string;
  opportunity_title: string;
}

interface FeedbackFormProps {
  toUserId: string;
  onSubmitted?: () => void;
}

export function FeedbackForm({ toUserId, onSubmitted }: FeedbackFormProps) {
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState("");
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.feedback
      .experiences(toUserId)
      .then((r) => {
        setExperiences(r.experiences);
        if (r.experiences.length === 1) {
          setSelectedId(r.experiences[0].opportunity_id);
        }
      })
      .catch(() => setExperiences([]))
      .finally(() => setLoading(false));
  }, [toUserId]);

  const selectedExp = experiences.find((e) => e.opportunity_id === selectedId);
  const opportunityType = selectedExp?.opportunity_type ?? "";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!opportunityType || !text.trim()) {
      setError("Please select a context and write your feedback.");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      await api.feedback.create({
        to_user_id: toUserId,
        opportunity_type: opportunityType,
        text: text.trim(),
      });
      setSubmitted(true);
      onSubmitted?.();
    } catch {
      setError("Failed to submit feedback. You may need to be logged in.");
      setSubmitting(false);
    }
  }

  if (submitted) {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6 text-center">
          <p className="text-green-800 font-medium">Thank you for your feedback!</p>
          <p className="text-sm text-green-600 mt-1">
            Your anonymous feedback helps the community make better connections.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Leave anonymous feedback</CardTitle>
          <p className="text-sm text-muted-foreground">
            Share your experience. Your identity will not be revealed.
          </p>
        </CardHeader>
        <CardContent>
          <div className="h-10 rounded bg-muted animate-pulse mb-4" />
          <div className="h-24 rounded bg-muted animate-pulse" />
        </CardContent>
      </Card>
    );
  }

  if (experiences.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            No interactions to leave feedback for.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Leave anonymous feedback</CardTitle>
        <p className="text-sm text-muted-foreground">
          Share your experience. Your identity will not be revealed.
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Context of your interaction</Label>
            {experiences.length === 1 ? (
              <div className="rounded-md border px-3 py-2 text-sm bg-muted/50">
                {TYPE_LABELS[experiences[0].opportunity_type] ?? experiences[0].opportunity_type} —{" "}
                {experiences[0].opportunity_title}
              </div>
            ) : (
              <Select value={selectedId} onValueChange={setSelectedId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select the interaction..." />
                </SelectTrigger>
                <SelectContent>
                  {experiences.map((e) => (
                    <SelectItem key={e.opportunity_id} value={e.opportunity_id}>
                      {TYPE_LABELS[e.opportunity_type] ?? e.opportunity_type}: {e.opportunity_title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Your feedback</Label>
              <VoiceInput onTranscript={setText} disabled={submitting} />
            </div>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Describe your experience working with, collaborating with, or meeting this person..."
              rows={4}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "Submitting..." : "Submit anonymous feedback"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
