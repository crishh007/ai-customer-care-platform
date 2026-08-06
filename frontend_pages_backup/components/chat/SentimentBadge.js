// ASSIGNED TO: FE-2
// Props: sentiment = 'happy' | 'frustrated' | 'angry' | 'neutral' | 'urgent' | 'confused'
// - Render colored pill badge based on sentiment value
// Color map: happy=green, frustrated=orange, angry=red, neutral=gray, urgent=purple

export default function SentimentBadge({ sentiment }) {
  return (
    <span>
      {/* TODO: Apply color class based on sentiment prop */}
      {sentiment}
    </span>
  )
}
