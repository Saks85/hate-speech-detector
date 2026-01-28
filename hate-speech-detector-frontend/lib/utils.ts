import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Returns a consistent badge variant for moderation labels.
 * hate       → red
 * offensive  → yellow
 * not_hate   → green
 * normal     → green
 */

export function normalizeLabel(
  label: string
): "hate" | "offensive" | "not_hate" | "normal" {
  const l = label.trim().toLowerCase()

  // Explicit safe / neutral labels FIRST
  if (l === "not hate" || l === "not_hate") return "not_hate"
  if (l === "normal") return "normal"

  // Offensive before hate
  if (l.includes("offensive")) return "offensive"

  // Hate LAST (most severe)
  if (l === "hate" || l.includes("hate speech")) return "hate"

  // Fallback
  return "not_hate"
}


export function getLabelVariant(label: string) {
  const canonical = normalizeLabel(label)

  switch (canonical) {
    case "hate":
      return "destructive" // red
    case "offensive":
      return "warning"   // yellow
    default:
      return "secondary"     //(not_hate, normal)
  }
}
/**
 * Formats labels for UI display
 * not_hate → Not Hate
 */
export function formatLabel(label: string) {
  return label
    .replace("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
