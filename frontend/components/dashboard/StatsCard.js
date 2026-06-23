// ASSIGNED TO: FE-3
// Props: title (string), value (string|number), change (string, e.g. '+12%'), icon
// - Single KPI metric card
// - Show trend arrow (up/down) based on change value

export default function StatsCard({ title, value, change, icon }) {
  return (
    <div>
      {/* TODO: Render stats card */}
      <h3>{title}</h3>
      <p>{value}</p>
    </div>
  )
}
