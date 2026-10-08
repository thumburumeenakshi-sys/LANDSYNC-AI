import { useEffect, useState } from "react";
import MapView from "./MapView";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [cadastralFile, setCadastralFile] = useState(null);
  const [droneFile, setDroneFile] = useState(null);
  const [gnssFile, setGnssFile] = useState(null);

  const [conflicts, setConflicts] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [backendOnline, setBackendOnline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  
const loadConflicts = async () => {
  try {
    const response = await fetch(`${API_URL}/conflicts`);

    if (!response.ok) {
      throw new Error("Backend request failed");
    }

    const data = await response.json();

    setConflicts(data.conflicts || []);
    setBackendOnline(true);
    setLastUpdated(new Date());
  } catch (error) {
    console.error("Unable to connect to backend:", error);
    setBackendOnline(false);
  }
};

useEffect(() => {
  const timer = setTimeout(() => {
    loadConflicts();
  }, 0);

  return () => clearTimeout(timer);
}, []);

  const processData = async () => {
    if (!cadastralFile || !droneFile || !gnssFile) {
      setMessage("Please select all three datasets before processing.");
      return;
    }

    setProcessing(true);
    setMessage("");

    const formData = new FormData();

    formData.append("cadastral", cadastralFile);
    formData.append("drone", droneFile);
    formData.append("gnss", gnssFile);

    try {
      const response = await fetch(`${API_URL}/process`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Processing failed");
      }

      setMessage(
        `LANDSYNC completed successfully. ${data.total_conflicts} conflicts detected.`
      );

      await loadConflicts();

      setActivePage("conflicts");
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setProcessing(false);
    }
  };

  const highRisk = conflicts.filter(
    (item) => item.risk_level === "HIGH"
  ).length;

  const mediumRisk = conflicts.filter(
    (item) => item.risk_level === "MEDIUM"
  ).length;

  const lowRisk = conflicts.filter(
    (item) => item.risk_level === "LOW"
  ).length;

  const renderPage = () => {
    if (activePage === "dashboard") {
      return (
        <Dashboard
          conflicts={conflicts}
          highRisk={highRisk}
          mediumRisk={mediumRisk}
          lowRisk={lowRisk}
          setActivePage={setActivePage}
        />
      );
    }

    if (activePage === "upload") {
      return (
        <UploadPage
          cadastralFile={cadastralFile}
          droneFile={droneFile}
          gnssFile={gnssFile}
          setCadastralFile={setCadastralFile}
          setDroneFile={setDroneFile}
          setGnssFile={setGnssFile}
          processData={processData}
          processing={processing}
          message={message}
        />
      );
    }

    if (activePage === "conflicts") {
      return (
        <ConflictsPage
          conflicts={conflicts}
        />
      );
    }

    if (activePage === "map") {
      return <MapPage />;
    }

    if (activePage === "ai") {
      return <AIPage conflicts={conflicts} />;
    }

    if (activePage === "reports") {
      return <ReportsPage conflicts={conflicts} />;
    }

    return null;
  };

  return (
    <div className="app-shell">

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-mark">L</div>

          <div>
            <div className="brand-name">
              LANDSYNC
            </div>

            <div className="brand-subtitle">
              AI LAND INTELLIGENCE
            </div>
          </div>
        </div>


        <nav className="sidebar-nav">

          <div className="nav-section">
            OVERVIEW
          </div>

          <NavItem
            icon="▦"
            label="Dashboard"
            active={activePage === "dashboard"}
            onClick={() => setActivePage("dashboard")}
          />


          <div className="nav-section">
            DATA & ANALYSIS
          </div>

          <NavItem
            icon="↑"
            label="Data Upload"
            active={activePage === "upload"}
            onClick={() => setActivePage("upload")}
          />

          <NavItem
            icon="⚠"
            label="Conflicts"
            active={activePage === "conflicts"}
            onClick={() => setActivePage("conflicts")}
            badge={conflicts.length}
          />

          <NavItem
            icon="◎"
            label="GIS Map"
            active={activePage === "map"}
            onClick={() => setActivePage("map")}
          />

          <NavItem
            icon="✦"
            label="AI Analysis"
            active={activePage === "ai"}
            onClick={() => setActivePage("ai")}
          />


          <div className="nav-section">
            OUTPUT
          </div>

          <NavItem
            icon="▤"
            label="Reports"
            active={activePage === "reports"}
            onClick={() => setActivePage("reports")}
          />

        </nav>


        <div className="sidebar-footer">

          <div className="system-status">
            <span className="status-dot"></span>

            <div>
          <strong>
  {backendOnline ? "Backend Connected" : "Backend Offline"}
</strong>
<small>
  {lastUpdated
    ? `Updated ${lastUpdated.toLocaleTimeString()}`
    : "Connecting to LANDSYNC API..."}
</small>  
            </div>
          </div>

        </div>

      </aside>


      <main className="main-content">

        <header className="topbar">

          <div>
            <div className="topbar-label">
              LAND DATA INTELLIGENCE PLATFORM
            </div>

            <h1>
              {getPageTitle(activePage)}
            </h1>
          </div>

          <button
            className="top-upload-button"
            onClick={() => setActivePage("upload")}
          >
            + Upload Dataset
          </button>

        </header>


        <div className="page-content">
          {renderPage()}
        </div>

      </main>

    </div>
  );
}


function getPageTitle(page) {
  const titles = {
    dashboard: "Dashboard",
    upload: "Dataset Upload",
    conflicts: "Conflict Detection",
    map: "Geospatial Intelligence",
    ai: "AI Conflict Analysis",
    reports: "LANDSYNC Reports",
  };

  return titles[page] || "LANDSYNC";
}


function NavItem({
  icon,
  label,
  active,
  onClick,
  badge,
}) {
  return (
    <button
      className={`nav-item ${active ? "active" : ""}`}
      onClick={onClick}
    >
      <span className="nav-icon">{icon}</span>

      <span>{label}</span>

      {badge !== undefined && (
        <span className="nav-badge">
          {badge}
        </span>
      )}
    </button>
  );
}


/* =================================================
   DASHBOARD
================================================= */

function Dashboard({
  conflicts,
  highRisk,
  mediumRisk,
  lowRisk,
  setActivePage,
}) {
  return (
    <div>

      <section className="hero-card">

        <div>

          <span className="eyebrow">
            INTELLIGENT LAND DATA HARMONIZATION
          </span>

          <h2>
            One Land.
            <br />
            Many Sources.
            <br />
            <span>One Trusted View.</span>
          </h2>

          <p>
            Harmonize cadastral, drone and GNSS
            observations to detect land-data conflicts,
            calculate risk and support human review.
          </p>

          <button
            className="primary-button"
            onClick={() => setActivePage("upload")}
          >
            Start Data Analysis →
          </button>

        </div>

        <div className="hero-visual">
          <div className="hero-circle">
            <span>LAND</span>
            <strong>AI</strong>
            <small>INTELLIGENCE</small>
          </div>
        </div>

      </section>


      <section className="stats-grid">

        <StatCard
          label="Total Conflicts"
          value={conflicts.length}
          icon="⚠"
        />

        <StatCard
          label="High Risk"
          value={highRisk}
          icon="!"
          danger
        />

        <StatCard
          label="Medium Risk"
          value={mediumRisk}
          icon="△"
        />

        <StatCard
          label="Low Risk"
          value={lowRisk}
          icon="✓"
          success
        />

      </section>


      <section className="dashboard-grid">

        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                CONFLICT MONITORING
              </span>

              <h3>
                Recent Conflicts
              </h3>
            </div>

            <button
              className="text-button"
              onClick={() => setActivePage("conflicts")}
            >
              View all →
            </button>

          </div>

          <ConflictTable
            conflicts={conflicts.slice(0, 5)}
          />

        </div>


        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                AI INSIGHTS
              </span>

              <h3>
                Review Required
              </h3>
            </div>

          </div>

          <div className="review-card">

            <div className="review-number">
              {highRisk}
            </div>

            <div>
              <strong>
                High-risk parcels
              </strong>

              <p>
                require human verification before
                the land record is trusted.
              </p>
            </div>

          </div>

          <button
            className="secondary-button full-width"
            onClick={() => setActivePage("ai")}
          >
            Open AI Analysis
          </button>

        </div>

      </section>


      <section className="panel map-preview-panel">

        <div className="panel-header">

          <div>
            <span className="eyebrow">
              GEOSPATIAL INTELLIGENCE
            </span>

            <h3>
              Parcel Conflict Map
            </h3>
          </div>

          <button
            className="text-button"
            onClick={() => setActivePage("map")}
          >
            Open full map →
          </button>

        </div>

        <MapView />

      </section>

    </div>
  );
}


function StatCard({
  label,
  value,
  icon,
  danger,
  success,
}) {
  return (
    <div className="stat-card">

      <div
        className={`stat-icon ${
          danger
            ? "danger"
            : success
            ? "success"
            : ""
        }`}
      >
        {icon}
      </div>

      <div>
        <div className="stat-value">
          {value}
        </div>

        <div className="stat-label">
          {label}
        </div>
      </div>

    </div>
  );
}


/* =================================================
   UPLOAD PAGE
================================================= */

function UploadPage({
  cadastralFile,
  droneFile,
  gnssFile,
  setCadastralFile,
  setDroneFile,
  setGnssFile,
  processData,
  processing,
  message,
}) {
  return (
    <div>

      <section className="page-intro">

        <span className="eyebrow">
          DATA INGESTION
        </span>

        <h2>
          Upload Land Data Sources
        </h2>

        <p>
          Upload independent land datasets.
          LANDSYNC will normalize, compare and
          score the records automatically.
        </p>

      </section>


      <section className="source-grid">

        <UploadCard
          number="01"
          title="Cadastral"
          description="Official parcel, owner, area and land-use records."
          accept=".csv"
          file={cadastralFile}
          setFile={setCadastralFile}
          icon="▣"
        />

        <UploadCard
          number="02"
          title="Drone Survey"
          description="Observed area, boundary deviation and land-cover data."
          accept=".csv"
          file={droneFile}
          setFile={setDroneFile}
          icon="◇"
        />

        <UploadCard
          number="03"
          title="GNSS Survey"
          description="Coordinate, elevation and positioning accuracy observations."
          accept=".csv"
          file={gnssFile}
          setFile={setGnssFile}
          icon="◎"
        />

      </section>


      <section className="processing-panel">

        <div className="processing-flow">

          <div className="flow-step">
            <span>1</span>
            Upload
          </div>

          <div className="flow-line"></div>

          <div className="flow-step">
            <span>2</span>
            Harmonize
          </div>

          <div className="flow-line"></div>

          <div className="flow-step">
            <span>3</span>
            Detect
          </div>

          <div className="flow-line"></div>

          <div className="flow-step">
            <span>4</span>
            Score
          </div>

          <div className="flow-line"></div>

          <div className="flow-step">
            <span>5</span>
            AI Review
          </div>

        </div>


        {message && (
          <div className="upload-message">
            {message}
          </div>
        )}


        <button
          className="process-button"
          onClick={processData}
          disabled={processing}
        >
          {processing
            ? "PROCESSING DATA..."
            : "PROCESS DATA →"}
        </button>

      </section>


      <section className="format-note">

        <strong>
          Supported demo format
        </strong>

        <span>
          CSV files with parcel_id as the common
          identifier across datasets.
        </span>

      </section>

    </div>
  );
}


function UploadCard({
  number,
  title,
  description,
  accept,
  file,
  setFile,
  icon,
}) {
  return (
    <label className="upload-card">

      <input
        type="file"
        accept={accept}
        onChange={(event) =>
          setFile(event.target.files[0])
        }
      />

      <div className="upload-number">
        {number}
      </div>

      <div className="upload-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {description}
      </p>

      <div className="file-select">
        {file
          ? `✓ ${file.name}`
          : "Choose CSV file"}
      </div>

      <small>
        Click to browse
      </small>

    </label>
  );
}


/* =================================================
   CONFLICTS
================================================= */

function ConflictsPage({ conflicts }) {
  return (
    <div>

      <section className="page-intro">

        <span className="eyebrow">
          CONFLICT ENGINE
        </span>

        <h2>
          Detected Land Conflicts
        </h2>

        <p>
          Cross-source discrepancies identified
          by the LANDSYNC engine.
        </p>

      </section>

      <div className="panel">

        <ConflictTable
          conflicts={conflicts}
          expanded
        />

      </div>

    </div>
  );
}

function ConflictTable({ conflicts }) {
  if (!conflicts.length) {
    return (
      <div className="empty-state">
        No conflicts detected yet.
        Upload datasets to begin analysis.
      </div>
    );
  }

  return (
    <div className="table-wrapper">

      <table>

        <thead>

          <tr>
            <th>Parcel</th>
            <th>Risk</th>
            <th>Confidence</th>
            <th>Area Δ</th>
            <th>Boundary Δ</th>
            <th>Status</th>
          </tr>

        </thead>

        <tbody>

          {conflicts.map((conflict, index) => (

            <tr key={`${conflict.parcel_id}-${index}`}>

              <td>
                <strong>
                  {conflict.parcel_id}
                </strong>
              </td>

              <td>
                <RiskBadge
                  risk={conflict.risk_level}
                />
              </td>

              <td>
                {conflict.confidence}%
              </td>

              <td>
                {conflict.area_difference_percentage}%
              </td>

              <td>
                {conflict.boundary_deviation_m} m
              </td>

              <td>
                <span className="status-text">
                  {conflict.status}
                </span>
              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}


function RiskBadge({ risk }) {
  return (
    <span
      className={`risk-badge ${risk.toLowerCase()}`}
    >
      <span></span>
      {risk}
    </span>
  );
}


/* =================================================
   MAP
================================================= */

function MapPage() {
  return (
    <div>

      <section className="page-intro">

        <span className="eyebrow">
          GEOSPATIAL INTELLIGENCE
        </span>

        <h2>
          Parcel Risk Map
        </h2>

        <p>
          Geographic view of detected land-data
          conflicts and risk levels.
        </p>

      </section>

      <section className="panel full-map-panel">
        <MapView />
      </section>

    </div>
  );
}


/* =================================================
   AI
================================================= */

function AIPage({ conflicts }) {
  return (
    <div>

      <section className="page-intro">

        <span className="eyebrow">
          EXPLAINABLE AI
        </span>

        <h2>
          AI Conflict Analysis
        </h2>

        <p>
          Explainable reasoning and recommended
          actions for detected discrepancies.
        </p>

      </section>


      <div className="ai-grid">

        {conflicts.map((conflict, index) => (

          <div
            className="ai-card"
            key={`${conflict.parcel_id}-${index}`}
          >

            <div className="ai-card-header">

              <div>
                <span className="eyebrow">
                  PARCEL
                </span>

                <h3>
                  {conflict.parcel_id}
                </h3>
              </div>

              <RiskBadge
                risk={conflict.risk_level}
              />

            </div>


            <div className="ai-metrics">

              <div>
                <small>
                  Confidence
                </small>

                <strong>
                  {conflict.confidence}%
                </strong>
              </div>

              <div>
                <small>
                  Area Difference
                </small>

                <strong>
                  {conflict.area_difference_percentage}%
                </strong>
              </div>

              <div>
                <small>
                  Boundary
                </small>

                <strong>
                  {conflict.boundary_deviation_m} m
                </strong>
              </div>

            </div>


            <div className="ai-section">

              <small>
                SYSTEM ASSESSMENT
              </small>

              <p>
                {getAIExplanation(conflict)}
              </p>

            </div>


            <div className="recommendation">

              <strong>
                Recommended Action
              </strong>

              <p>
                {getRecommendation(conflict)}
              </p>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}


function getAIExplanation(conflict) {
  if (conflict.risk_level === "HIGH") {
    return `Parcel ${conflict.parcel_id} shows a significant multi-source discrepancy. Immediate human review is recommended.`;
  }

  if (conflict.risk_level === "MEDIUM") {
    return `Parcel ${conflict.parcel_id} shows a moderate discrepancy requiring verification against the latest authorized survey.`;
  }

  return `Parcel ${conflict.parcel_id} shows a minor variation suitable for routine monitoring.`;
}


function getRecommendation(conflict) {
  if (conflict.risk_level === "HIGH") {
    return "Compare the official cadastral boundary with the latest authorized survey and drone evidence.";
  }

  if (conflict.risk_level === "MEDIUM") {
    return "Verify the parcel against the latest survey or geospatial record.";
  }

  return "Continue monitoring during the next routine land-record update.";
}


/* =================================================
   REPORTS
================================================= */

function ReportsPage({ conflicts }) {

  const high = conflicts.filter(
    (c) => c.risk_level === "HIGH"
  ).length;

  const medium = conflicts.filter(
    (c) => c.risk_level === "MEDIUM"
  ).length;

  const low = conflicts.filter(
    (c) => c.risk_level === "LOW"
  ).length;

  return (
    <div>

      <section className="page-intro">

        <span className="eyebrow">
          DECISION SUPPORT
        </span>

        <h2>
          LANDSYNC Report
        </h2>

        <p>
          Summary of the current multi-source
          harmonization analysis.
        </p>

      </section>


      <section className="report-header">

        <div>
          <span className="eyebrow">
            ANALYSIS SUMMARY
          </span>

          <h2>
            Land Data Harmonization Report
          </h2>

          <p>
            Generated from cadastral, drone and
            GNSS observations.
          </p>
        </div>

        <div className="report-total">
          <strong>
            {conflicts.length}
          </strong>

          <span>
            Conflicts
          </span>
        </div>

      </section>


      <section className="report-grid">

        <ReportMetric
          label="High Risk"
          value={high}
          description="Human review required"
        />

        <ReportMetric
          label="Medium Risk"
          value={medium}
          description="Verification required"
        />

        <ReportMetric
          label="Low Risk"
          value={low}
          description="Routine monitoring"
        />

      </section>


      <section className="panel">

        <div className="panel-header">

          <div>
            <span className="eyebrow">
              DECISION QUEUE
            </span>

            <h3>
              Human Review Candidates
            </h3>
          </div>

        </div>

        <ConflictTable
          conflicts={conflicts.filter(
            (c) => c.risk_level === "HIGH"
          )}
        />

      </section>

    </div>
  );
}


function ReportMetric({
  label,
  value,
  description,
}) {
  return (
    <div className="report-metric">

      <strong>
        {value}
      </strong>

      <span>
        {label}
      </span>

      <small>
        {description}
      </small>

    </div>
  );
}


export default App;