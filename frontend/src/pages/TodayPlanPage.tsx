const TodayPlanPage = () => {
  return (
    <section id="today" className="panel subtle">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Today&apos;s plan</p>
          <h2>Protect time for the important work</h2>
          <p className="muted">
            Slot focused blocks, add quick notes, and let the AI manager keep you on pace.
          </p>
        </div>
      </header>

      <div className="plan-grid">
        <article className="plan-card">
          <p className="pill in-progress">08:00 - 10:00</p>
          <h3>Deep work: spec writing</h3>
          <p className="muted">Keep notifications off. Ship the first draft.</p>
        </article>
        <article className="plan-card">
          <p className="pill todo">10:30 - 11:00</p>
          <h3>Standup + sync</h3>
          <p className="muted">Share blockers and update the AI Time Manager backlog.</p>
        </article>
        <article className="plan-card">
          <p className="pill done">14:00 - 15:00</p>
          <h3>QA round</h3>
          <p className="muted">Review flows and align with the backend API responses.</p>
        </article>
      </div>
    </section>
  )
}

export default TodayPlanPage
