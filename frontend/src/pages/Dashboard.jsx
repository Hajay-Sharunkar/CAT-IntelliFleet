import "./Dashboard.css";

export default function Dashboard() {
  return (
    <main className="dashboard">

      <div className="dashboard-header">
        <p className="eyebrow">FLEET OPERATIONS</p>
        <h1>Fleet Dashboard</h1>
        <p className="subtitle">
          Monitor your equipment and fleet operations.
        </p>
      </div>

      {/* Fleet Overview */}
      <section className="fleet-section">
        <h2>Fleet Overview</h2>

        <div className="fleet-overview">

          <div className="stat-card">
            <p>Total Fleet</p>
            <h3>20</h3>
            <span>Registered machines</span>
          </div>

          <div className="stat-card">
            <p>Active</p>
            <h3>14</h3>
            <span>Currently operating</span>
          </div>

          <div className="stat-card">
            <p>Idle</p>
            <h3>4</h3>
            <span>Not currently productive</span>
          </div>

          <div className="stat-card">
            <p>Attention</p>
            <h3>2</h3>
            <span>Needs review</span>
          </div>

        </div>
      </section>

      {/* Attention Required */}
      <section className="attention-section">

        <div className="section-header">
          <div>
            <p className="eyebrow">NEEDS ATTENTION</p>
            <h2>Priority Issues</h2>
          </div>

          <button className="view-all-button">
            View all →
          </button>
        </div>

        <div className="alert-card">

          <div className="alert-main">

            <div className="alert-title-row">
              <span className="severity-high">HIGH</span>
              <span className="alert-time">8 min ago</span>
            </div>

            <h3>EQX1007</h3>

            <p className="alert-name">
              Excessive idle time
            </p>

            <p className="alert-description">
              Machine has remained idle during an active rental
              with no operator assigned.
            </p>

          </div>

          <div className="alert-details">

            <div>
              <span>Idle time</span>
              <strong>12 hrs</strong>
            </div>

            <div>
              <span>Operator</span>
              <strong>Not assigned</strong>
            </div>

            <div>
              <span>Rental ends</span>
              <strong>Sep 2</strong>
            </div>

          </div>

          <button className="details-button">
            View details →
          </button>

        </div>

      </section>

    </main>
  );
}