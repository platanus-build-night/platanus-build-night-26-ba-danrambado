"use client";

import { useState } from "react";
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

const CONTEXT_OPTIONS = [
  { value: "project", label: "Project" },
  { value: "collab", label: "Collaboration" },
  { value: "date", label: "Date" },
  { value: "help", label: "Help / Mentoring" },
  { value: "job", label: "Job / Work" },
];

interface FeedbackFormProps {
  toUserId: string;
  onSubmitted?: () => void;
}

export function FeedbackForm({ toUserId, onSubmitted }: FeedbackFormProps) {
  const [context, setContext] = useState("");
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!context || !text.trim()) {
      setError("Please select a context and write your feedback.");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      await api.feedback.create({
        to_user_id: toUserId,
        opportunity_type: context,
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
            <Select value={context} onValueChange={setContext}>
              <SelectTrigger>
                <SelectValue placeholder="How did you interact?" />
              </SelectTrigger>
              <SelectContent>
                {CONTEXT_OPTIONS.map((o) => (
                  <SelectItem key={o.value} value={o.value}>
                    {o.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
