import { useState } from "react";

const fleetStats = {
  active: 14,
  idle: 4,
  overdue: 2,
  maintenance: 2,
};

const alerts = [
  {
    id: 1,
    machine: "EQX1007",
    severity: "HIGH",
    title: "Excessive idle time",
    description:
      "Machine has remained idle during an active rental with no operator assigned.",
    idle: "12 hrs",
    operator: "Unassigned",
    site: "Site A",
    time: "8 min ago",
  },
  {
    id: 2,
    machine: "EQX1002",
    severity: "MEDIUM",
    title: "Missing site assignment",
    description:
      "Equipment currently has no assigned operating site or operator.",
    idle: "9 hrs",
    operator: "Unassigned",
    site: "Unassigned",
    time: "32 min ago",
  },
  {
    id: 3,
    machine: "EQX1004",
    severity: "LOW",
    title: "Low utilization",
    description:
      "Machine utilization is below the expected operating threshold.",
    idle: "9 hrs",
    operator: "K. Verma",
    site: "Site C",
    time: "1 hr ago",
  },
];

const demand = [
  {
    site: "Site B",
    equipment: "Excavator",
    score: 7.8,
    level: "HIGH",
  },
  {
    site: "Site C",
    equipment: "Loader",
    score: 5.1,
    level: "MEDIUM",
  },
  {
    site: "Site A",
    equipment: "Dozer",
    score: 3.2,
    level: "LOW",
  },
];

const recommendations = [
  {
    machine: "EQX1007",
    action: "Consider reassignment to Site B",
    reason:
      "The machine is under-utilized at Site A while Site B shows higher excavator demand.",
    impact: "Reduce idle time",
    savings: "₹48,000",
    confidence: "High",
  },
  {
    machine: "DZR3010",
    action: "Prepare rental return",
    reason:
      "Rental period is approaching its end while utilization remains low.",
    impact: "Avoid unnecessary rental days",
    savings: "₹24,000",
    confidence: "High",
  },
];

const machines = [
  {
    id: "EQX1001",
    type: "Excavator",
    status: "Active",
    site: "Site A",
    operator: "R. Sharma",
    utilization: "82%",
    idle: "2 hrs",
    fuel: "74%",
    rental: "Active",
  },
  {
    id: "EQX1002",
    type: "Excavator",
    status: "Idle",
    site: "Unassigned",
    operator: "Unassigned",
    utilization: "18%",
    idle: "9 hrs",
    fuel: "61%",
    rental: "Active",
  },
  {
    id: "EQX1004",
    type: "Dozer",
    status: "Idle",
    site: "Site C",
    operator: "K. Verma",
    utilization: "22%",
    idle: "9 hrs",
    fuel: "55%",
    rental: "Active",
  },
  {
    id: "EQX1007",
    type: "Excavator",
    status: "Alert",
    site: "Site A",
    operator: "Unassigned",
    utilization: "12%",
    idle: "12 hrs",
    fuel: "62%",
    rental: "Ending Soon",
  },
  {
    id: "LDR2003",
    type: "Loader",
    status: "Active",
    site: "Site B",
    operator: "A. Kumar",
    utilization: "91%",
    idle: "1 hr",
    fuel: "81%",
    rental: "Active",
  },
];

const telemetry = [
  {
    machine: "EQX1007",
    engine: "210 hrs",
    idle: "12 hrs",
    fuel: "62%",
    status: "Idle",
    temperature: "82°C",
    site: "Site A",
  },
  {
    machine: "EQX1001",
    engine: "340 hrs",
    idle: "2 hrs",
    fuel: "74%",
    status: "Running",
    temperature: "76°C",
    site: "Site A",
  },
  {
    machine: "LDR2003",
    engine: "185 hrs",
    idle: "1 hr",
    fuel: "81%",
    status: "Running",
    temperature: "73°C",
    site: "Site B",
  },
];
const rentals = [
  {
    id: "R-1001",
    machine: "EQX1001",
    type: "Excavator",
    site: "Site A",
    start: "Aug 18, 2026",
    end: "Sep 12, 2026",
    status: "Active",
    dailyRate: "₹18,000",
  },
  {
    id: "R-1002",
    machine: "EQX1007",
    type: "Excavator",
    site: "Site A",
    start: "Aug 10, 2026",
    end: "Sep 2, 2026",
    status: "Ending Soon",
    dailyRate: "₹22,000",
  },
  {
    id: "R-1003",
    machine: "EQX1002",
    type: "Excavator",
    site: "Site B",
    start: "Aug 22, 2026",
    end: "Sep 18, 2026",
    status: "Active",
    dailyRate: "₹20,000",
  },
  {
    id: "R-1004",
    machine: "DZR3010",
    type: "Dozer",
    site: "Site C",
    start: "Aug 1, 2026",
    end: "Aug 30, 2026",
    status: "Overdue",
    dailyRate: "₹16,000",
  },
  {
    id: "R-1005",
    machine: "LDR2003",
    type: "Loader",
    site: "Site B",
    start: "Aug 25, 2026",
    end: "Sep 20, 2026",
    status: "Active",
    dailyRate: "₹15,000",
  },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [notifications, setNotifications] = useState(true);

  const navigation = [
    {
      title: "OPERATIONS",
      items: ["Dashboard", "Fleet", "Rentals", "Telemetry"],
    },
    {
      title: "MANAGEMENT",
      items: [
        "Maintenance",
        "Alerts",
        "Recommendations",
        "Analytics",
        "Users",
      ],
    },
  ];

  const pageTitle =
    activePage === "Dashboard"
      ? "Fleet Command Center"
      : activePage;

  return (
    <>
      <style>{`
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          font-family: Inter, Arial, Helvetica, sans-serif;
          background: #f5f6f4;
          color: #20252b;
        }

        button {
          font-family: inherit;
        }

        .app {
          min-height: 100vh;
          display: flex;
          background: #f5f6f4;
        }

        .sidebar {
          width: 250px;
          min-height: 100vh;
          background: #181b1e;
          color: white;
          padding: 22px 15px;
          display: flex;
          flex-direction: column;
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 5px 8px 24px;
          border-bottom: 1px solid #303438;
        }

        .brand-mark {
          width: 43px;
          height: 43px;
          background: #f2b705;
          color: #181b1e;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
          font-weight: 900;
          font-size: 12px;
        }

        .brand h2 {
          margin: 0;
          font-size: 19px;
        }

        .brand span {
          color: #90979d;
          font-size: 10px;
        }

        .navigation {
          margin-top: 18px;
        }

        .nav-label {
          margin: 19px 10px 7px;
          color: #70777d;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .13em;
        }

        .nav-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 12px;
          border: 0;
          background: transparent;
          color: #aeb4b9;
          padding: 11px 12px;
          border-radius: 8px;
          cursor: pointer;
          font-size: 12px;
          text-align: left;
          margin-bottom: 3px;
        }

        .nav-item:hover {
          background: #252a2e;
          color: white;
        }

        .nav-item.active {
          background: #2b3034;
          color: white;
        }

        .nav-icon {
          width: 18px;
          text-align: center;
          color: #8c949a;
        }

        .nav-item.active .nav-icon {
          color: #f2b705;
        }

        .sidebar-footer {
          margin-top: auto;
          border-top: 1px solid #303438;
          padding: 15px 10px 5px;
          display: flex;
          align-items: center;
          gap: 8px;
          color: #92999e;
          font-size: 10px;
        }

        .online-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #45a86b;
        }

        .main {
          margin-left: 250px;
          width: calc(100% - 250px);
          min-height: 100vh;
        }

        .topbar {
          height: 82px;
          background: white;
          border-bottom: 1px solid #e2e5e7;
          padding: 0 34px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .breadcrumb {
          margin: 0 0 5px;
          color: #8b9399;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .1em;
        }

        .topbar h1 {
          margin: 0;
          font-size: 19px;
          letter-spacing: -.02em;
        }

        .topbar-right {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .notification-button {
          position: relative;
          border: 0;
          background: transparent;
          cursor: pointer;
          font-size: 17px;
        }

        .notification-dot {
          position: absolute;
          top: 0;
          right: 0;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #d64545;
        }

        .user {
          display: flex;
          align-items: center;
          gap: 9px;
        }

        .avatar {
          width: 34px;
          height: 34px;
          border-radius: 50%;
          background: #eceeeb;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          font-weight: 800;
        }

        .user strong {
          display: block;
          font-size: 11px;
        }

        .user span {
          display: block;
          color: #8b9399;
          font-size: 9px;
          margin-top: 2px;
        }

        .content {
          padding: 32px 34px 50px;
          max-width: 1600px;
        }

        .welcome {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          margin-bottom: 30px;
        }

        .welcome h2 {
          margin: 0 0 6px;
          font-size: 25px;
          letter-spacing: -.03em;
        }

        .welcome p {
          margin: 0;
          color: #747c82;
          font-size: 12px;
        }

        .refresh-button {
          border: 1px solid #d9dddf;
          background: white;
          padding: 9px 13px;
          border-radius: 7px;
          cursor: pointer;
          color: #4b5359;
          font-size: 11px;
        }

        .section {
          margin-bottom: 34px;
        }

        .section-heading {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          margin-bottom: 14px;
        }

        .section-label {
          margin: 0 0 5px;
          color: #8a9298;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .12em;
        }

        .section-heading h2 {
          margin: 0;
          font-size: 17px;
        }

        .updated {
          color: #969da2;
          font-size: 10px;
        }

        .metric-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
        }

        .metric {
          background: white;
          border: 1px solid #e1e5e7;
          border-radius: 11px;
          padding: 20px;
          min-height: 135px;
        }

        .metric-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .metric-title {
          color: #777f85;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .08em;
        }

        .metric-icon {
          width: 24px;
          height: 24px;
          border-radius: 6px;
          background: #f0f1ef;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
        }

        .metric-value {
          display: block;
          margin-top: 18px;
          font-size: 31px;
          line-height: 1;
          letter-spacing: -.04em;
        }

        .metric-description {
          margin: 8px 0 0;
          color: #969da2;
          font-size: 10px;
        }

        .alert-list {
          display: flex;
          flex-direction: column;
          gap: 9px;
        }

        .alert {
          background: white;
          border: 1px solid #e1e5e7;
          border-radius: 11px;
          padding: 17px 19px;
          display: grid;
          grid-template-columns: 4px minmax(250px, 1fr) 100px 130px auto;
          align-items: center;
          gap: 20px;
        }

        .alert-line {
          height: 50px;
          border-radius: 5px;
        }

        .high-line {
          background: #c83d3d;
        }

        .medium-line {
          background: #c58a21;
        }

        .low-line {
          background: #7b8389;
        }

        .severity {
          font-size: 8px;
          font-weight: 900;
          letter-spacing: .08em;
        }

        .high {
          color: #b42318;
        }

        .medium {
          color: #a15c00;
        }

        .low {
          color: #667085;
        }

        .alert-time {
          margin-left: 9px;
          color: #9ba2a7;
          font-size: 9px;
        }

        .alert-machine {
          margin: 7px 0 3px;
          font-size: 14px;
        }

        .alert-title {
          margin: 0;
          font-size: 11px;
          font-weight: 600;
        }

        .alert-description {
          margin: 5px 0 0;
          color: #7d858b;
          font-size: 10px;
          line-height: 1.45;
        }

        .alert-data span {
          display: block;
          color: #9ba2a7;
          font-size: 8px;
          text-transform: uppercase;
          letter-spacing: .05em;
        }

        .alert-data strong {
          display: block;
          margin-top: 5px;
          color: #3d454b;
          font-size: 10px;
        }

        .outline-button {
          border: 1px solid #d5dade;
          background: white;
          color: #3f474d;
          border-radius: 7px;
          padding: 9px 12px;
          font-size: 10px;
          font-weight: 600;
          cursor: pointer;
          white-space: nowrap;
        }

        .outline-button:hover {
          background: #f5f6f4;
        }

        .two-column {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 14px;
        }

        .panel {
          background: white;
          border: 1px solid #e1e5e7;
          border-radius: 11px;
          padding: 20px;
        }

        .map {
          height: 260px;
          border-radius: 8px;
          background:
            linear-gradient(145deg, transparent 45%, #dfe3df 46%, transparent 47%),
            linear-gradient(30deg, transparent 45%, #e5e8e5 46%, transparent 47%),
            #f1f3f0;
          position: relative;
          overflow: hidden;
        }

        .site {
          position: absolute;
          background: white;
          border: 1px solid #d9ddda;
          border-radius: 7px;
          padding: 7px 9px;
          font-size: 9px;
          box-shadow: 0 2px 7px rgba(0,0,0,.04);
        }

        .site-a {
          left: 18%;
          top: 25%;
        }

        .site-b {
          right: 17%;
          top: 30%;
        }

        .site-c {
          left: 42%;
          bottom: 18%;
        }

        .site strong {
          display: block;
          font-size: 10px;
        }

        .site span {
          color: #8b9399;
          font-size: 8px;
        }

        .machine-dot {
          position: absolute;
          width: 9px;
          height: 9px;
          background: #f2b705;
          border: 2px solid white;
          border-radius: 50%;
          box-shadow: 0 1px 4px rgba(0,0,0,.2);
        }

        .dot1 {
          left: 30%;
          top: 48%;
        }

        .dot2 {
          right: 28%;
          top: 53%;
        }

        .dot3 {
          left: 55%;
          bottom: 30%;
        }

        .utilization-value {
          font-size: 42px;
          font-weight: 700;
          letter-spacing: -.05em;
          margin-top: 18px;
        }

        .utilization-subtitle {
          color: #899197;
          font-size: 10px;
        }

        .progress {
          height: 8px;
          background: #e9ece9;
          border-radius: 20px;
          margin: 25px 0 10px;
          overflow: hidden;
        }

        .progress-fill {
          width: 78%;
          height: 100%;
          background: #30363b;
          border-radius: 20px;
        }

        .utilization-footer {
          display: flex;
          justify-content: space-between;
          color: #7c858b;
          font-size: 9px;
        }

        .demand-list {
          display: flex;
          flex-direction: column;
          gap: 13px;
          margin-top: 19px;
        }

        .demand-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-bottom: 12px;
          border-bottom: 1px solid #eef0ee;
        }

        .demand-row:last-child {
          border-bottom: 0;
        }

        .demand-site {
          font-size: 11px;
          font-weight: 700;
        }

        .demand-equipment {
          margin-top: 4px;
          color: #8c9499;
          font-size: 9px;
        }

        .demand-right {
          text-align: right;
        }

        .demand-score {
          font-size: 16px;
          font-weight: 700;
        }

        .demand-level {
          display: block;
          margin-top: 2px;
          font-size: 8px;
          font-weight: 800;
          letter-spacing: .08em;
        }

        .shortage {
          margin-top: 18px;
          padding: 12px;
          background: #f7f8f6;
          border-left: 3px solid #c58a21;
          border-radius: 5px;
          font-size: 10px;
        }

        .shortage strong {
          display: block;
          margin-bottom: 4px;
        }

        .shortage span {
          color: #747c82;
        }

        .recommendations {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }

        .recommendation {
          background: white;
          border: 1px solid #e1e5e7;
          border-radius: 11px;
          padding: 19px;
        }

        .recommendation-machine {
          color: #7d858b;
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .08em;
        }

        .recommendation h3 {
          margin: 8px 0 7px;
          font-size: 14px;
        }

        .recommendation p {
          color: #737c82;
          font-size: 10px;
          line-height: 1.5;
          margin: 0;
        }

        .recommendation-bottom {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          margin-top: 18px;
        }

        .impact span,
        .savings span {
          display: block;
          color: #9ba2a7;
          font-size: 8px;
        }

        .impact strong,
        .savings strong {
          display: block;
          margin-top: 4px;
          font-size: 11px;
        }

        .savings {
          text-align: right;
        }

        .savings strong {
          font-size: 14px;
        }

        .business-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
        }

        .business-card {
          background: white;
          border: 1px solid #e1e5e7;
          border-radius: 11px;
          padding: 19px;
        }

        .business-card span {
          color: #8b9399;
          font-size: 9px;
        }

        .business-card strong {
          display: block;
          margin-top: 9px;
          font-size: 22px;
        }

        .business-card small {
          display: block;
          margin-top: 6px;
          color: #969da2;
          font-size: 9px;
        }

        /* FLEET PAGE */

        .fleet-summary {
          display: flex;
          gap: 10px;
          margin-top: 4px;
          color: #8a9298;
          font-size: 10px;
        }

        .fleet-summary span {
          padding-right: 10px;
          border-right: 1px solid #d9dddf;
        }

        .fleet-summary span:last-child {
          border: 0;
        }

        .fleet-toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          margin-bottom: 15px;
        }

        .search-input {
          width: 300px;
          padding: 10px 12px;
          border: 1px solid #d9dddf;
          border-radius: 7px;
          background: white;
          outline: none;
          font-size: 11px;
        }

        .search-input:focus {
          border-color: #aab1b5;
        }

        .filter-select {
          padding: 10px 12px;
          border: 1px solid #d9dddf;
          border-radius: 7px;
          background: white;
          color: #4b5359;
          font-size: 11px;
        }

        .fleet-table {
          background: white;
          border: 1px solid #e1e5e7;
          border-radius: 11px;
          overflow: hidden;
        }

        .fleet-table table {
          width: 100%;
          border-collapse: collapse;
        }

        .fleet-table th {
          background: #f8f9f8;
          color: #858d93;
          text-align: left;
          padding: 13px 15px;
          font-size: 8px;
          text-transform: uppercase;
          letter-spacing: .06em;
        }

        .fleet-table td {
          padding: 15px;
          border-top: 1px solid #edf0ee;
          font-size: 10px;
        }

        .machine-id {
          font-weight: 700;
          font-size: 11px;
        }

        .machine-type {
          color: #8a9298;
          margin-top: 3px;
          font-size: 9px;
        }

        .status-badge {
          display: inline-block;
          padding: 5px 8px;
          border-radius: 5px;
          background: #f0f2ef;
          font-size: 8px;
          font-weight: 800;
        }

        .status-active {
          color: #287a4b;
          background: #edf7f0;
        }

        .status-idle {
          color: #896314;
          background: #faf5e7;
        }

        .status-alert {
          color: #a52b2b;
          background: #fbeeee;
        }

        .utilization-cell {
          min-width: 100px;
        }

        .mini-progress {
          height: 5px;
          background: #e9ece9;
          border-radius: 10px;
          overflow: hidden;
          margin-top: 6px;
        }

        .mini-progress-fill {
          height: 100%;
          background: #596168;
        }

        /* RESPONSIVE */

        @media (max-width: 1100px) {

          .metric-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .two-column {
            grid-template-columns: 1fr;
          }

          .alert {
            grid-template-columns: 4px 1fr 1fr;
          }

          .recommendations {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 700px) {

          .sidebar {
            width: 70px;
            padding: 15px 8px;
          }

          .brand {
            justify-content: center;
          }

          .brand > div:last-child,
          .nav-label,
          .sidebar-footer {
            display: none;
          }

          .nav-item {
            justify-content: center;
            font-size: 0;
          }

          .nav-icon {
            font-size: 14px;
          }

          .main {
            margin-left: 70px;
            width: calc(100% - 70px);
          }

          .topbar {
            padding: 0 18px;
          }

          .content {
            padding: 24px 18px;
          }

          .metric-grid {
            grid-template-columns: 1fr;
          }

          .alert {
            grid-template-columns: 4px 1fr;
          }

          .alert-data {
            display: none;
          }

          .user-info {
            display: none;
          }

          .business-grid {
            grid-template-columns: 1fr;
          }

          .welcome {
            align-items: flex-start;
            flex-direction: column;
            gap: 15px;
          }

          .fleet-toolbar {
            flex-direction: column;
            align-items: stretch;
          }

          .search-input {
            width: 100%;
          }

        }
      `}</style>

      <div className="app">

        <aside className="sidebar">

          <div className="brand">
            <div className="brand-mark">CAT</div>

            <div>
              <h2>FleetIQ</h2>
              <span>Command Center</span>
            </div>
          </div>

          <nav className="navigation">

            {navigation.map((group, groupIndex) => (
              <div key={group.title}>

                <p className="nav-label">
                  {group.title}
                </p>

                {group.items.map((item, itemIndex) => {

                  const icons = [
                    "▦",
                    "▣",
                    "↔",
                    "◉",
                    "⚙",
                    "⚠",
                    "✦",
                    "▥",
                    "♙",
                  ];

                  const iconIndex =
                    groupIndex === 0
                      ? itemIndex
                      : itemIndex + navigation[0].items.length;

                  return (
                    <button
                      key={item}
                      className={`nav-item ${
                        activePage === item ? "active" : ""
                      }`}
                      onClick={() => setActivePage(item)}
                    >
                      <span className="nav-icon">
                        {icons[iconIndex]}
                      </span>

                      {item}
                    </button>
                  );
                })}

              </div>
            ))}

          </nav>

          <div className="sidebar-footer">
            <span className="online-dot"></span>
            System operational
          </div>

        </aside>


        <div className="main">

          <header className="topbar">

            <div>
              <p className="breadcrumb">
                OPERATIONS / {activePage.toUpperCase()}
              </p>

              <h1>{pageTitle}</h1>
            </div>

            <div className="topbar-right">

              <button
                className="notification-button"
                onClick={() => setNotifications(!notifications)}
              >
                🔔

                {notifications && (
                  <span className="notification-dot"></span>
                )}
              </button>

              <div className="user">

                <div className="avatar">
                  FM
                </div>

                <div className="user-info">
                  <strong>Fleet Manager</strong>
                  <span>Operations</span>
                </div>

              </div>

            </div>

          </header>


          <main className="content">

            {activePage === "Dashboard" && (
              <Dashboard />
            )}

            {activePage === "Fleet" && (
              <FleetPage />
            )}

            {activePage === "Telemetry" && (
              <TelemetryPage />
            )}

            {activePage === "Alerts" && (
              <AlertsPage />
            )}

            {activePage === "Recommendations" && (
              <RecommendationsPage />
            )}

            {activePage !== "Dashboard" &&
              activePage !== "Fleet" &&
              activePage !== "Telemetry" &&
              activePage !== "Alerts" &&
              activePage !== "Recommendations" && (
                <PlaceholderPage title={activePage} />
              )}

          </main>

        </div>

      </div>
    </>
  );
}


/* DASHBOARD */

function Dashboard() {
  return (
    <>

      <div className="welcome">

        <div>
          <h2>Good morning</h2>

          <p>
            Here's what's happening across your rental fleet.
          </p>
        </div>

        <button className="refresh-button">
          ↻ Refresh data
        </button>

      </div>


      <section className="section">

        <div className="section-heading">

          <div>
            <p className="section-label">
              FLEET STATUS
            </p>

            <h2>Fleet Overview</h2>
          </div>

          <span className="updated">
            Updated just now
          </span>

        </div>


        <div className="metric-grid">

          <Metric
            title="ACTIVE MACHINES"
            value={fleetStats.active}
            description="Currently operating"
            icon="●"
          />

          <Metric
            title="IDLE MACHINES"
            value={fleetStats.idle}
            description="Not currently productive"
            icon="Ⅱ"
          />

          <Metric
            title="OVERDUE RENTALS"
            value={fleetStats.overdue}
            description="Require immediate action"
            icon="!"
          />

          <Metric
            title="IN MAINTENANCE"
            value={fleetStats.maintenance}
            description="Currently in workshop"
            icon="⚙"
          />

        </div>

      </section>


      <section className="section">

        <div className="section-heading">

          <div>
            <p className="section-label">
              ACTION REQUIRED
            </p>

            <h2>Operational Alerts</h2>
          </div>

          <button className="outline-button">
            View all alerts →
          </button>

        </div>


        <div className="alert-list">

          {alerts.map((alert) => (
            <AlertItem
              key={alert.id}
              alert={alert}
            />
          ))}

        </div>

      </section>


      <div className="two-column section">

        <section className="panel">

          <div className="section-heading">

            <div>
              <p className="section-label">
                FLEET LOCATION
              </p>

              <h2>Live Fleet Overview</h2>
            </div>

            <span className="updated">
              ● Live
            </span>

          </div>

          <div className="map">

            <div className="site site-a">
              <strong>Site A</strong>
              <span>6 machines</span>
            </div>

            <div className="site site-b">
              <strong>Site B</strong>
              <span>8 machines</span>
            </div>

            <div className="site site-c">
              <strong>Site C</strong>
              <span>4 machines</span>
            </div>

            <span className="machine-dot dot1"></span>
            <span className="machine-dot dot2"></span>
            <span className="machine-dot dot3"></span>

          </div>

        </section>


        <section className="panel">

          <div className="section-heading">

            <div>
              <p className="section-label">
                FLEET HEALTH
              </p>

              <h2>Utilization</h2>
            </div>

            <span className="updated">
              Last 7 days
            </span>

          </div>

          <div className="utilization-value">
            78%
          </div>

          <div className="utilization-subtitle">
            Overall fleet utilization
          </div>

          <div className="progress">
            <div className="progress-fill"></div>
          </div>

          <div className="utilization-footer">
            <span>Productive 78%</span>
            <span>Idle 22%</span>
          </div>

        </section>

      </div>


      <section className="section">

        <div className="section-heading">

          <div>
            <p className="section-label">
              FORECAST
            </p>

            <h2>Demand Outlook</h2>
          </div>

          <button className="outline-button">
            Open forecast →
          </button>

        </div>


        <div className="panel">

          <div className="demand-list">

            {demand.map((item) => (
              <div
                className="demand-row"
                key={item.site}
              >

                <div>
                  <div className="demand-site">
                    {item.site}
                  </div>

                  <div className="demand-equipment">
                    {item.equipment} demand
                  </div>
                </div>

                <div className="demand-right">

                  <div className="demand-score">
                    {item.score}
                  </div>

                  <span
                    className={`demand-level ${
                      item.level === "HIGH"
                        ? "high"
                        : item.level === "MEDIUM"
                        ? "medium"
                        : "low"
                    }`}
                  >
                    {item.level}
                  </span>

                </div>

              </div>
            ))}

          </div>

          <div className="shortage">

            <strong>
              Potential shortage
            </strong>

            <span>
              Site B may require 2 additional excavators.
            </span>

          </div>

        </div>

      </section>


      <section className="section">

        <div className="section-heading">

          <div>
            <p className="section-label">
              DECISION SUPPORT
            </p>

            <h2>AI Decision Center</h2>
          </div>

          <span className="updated">
            Explainable recommendations
          </span>

        </div>


        <div className="recommendations">

          {recommendations.map((item) => (
            <div
              className="recommendation"
              key={item.machine}
            >

              <div className="recommendation-machine">
                {item.machine}
              </div>

              <h3>
                {item.action}
              </h3>

              <p>
                {item.reason}
              </p>

              <div className="recommendation-bottom">

                <div className="impact">
                  <span>EXPECTED IMPACT</span>
                  <strong>{item.impact}</strong>
                </div>

                <div className="savings">
                  <span>ESTIMATED SAVING</span>
                  <strong>{item.savings}</strong>
                </div>

              </div>

            </div>
          ))}

        </div>

      </section>


      <section className="section">

        <div className="section-heading">

          <div>
            <p className="section-label">
              BUSINESS IMPACT
            </p>

            <h2>Business Insights</h2>
          </div>

        </div>


        <div className="business-grid">

          <BusinessCard
            title="Estimated Cost Saved"
            value="₹1,84,000"
            description="Current demo estimate"
          />

          <BusinessCard
            title="Potential Idle Cost"
            value="₹96,000"
            description="Recoverable fleet capacity"
          />

          <BusinessCard
            title="Rental Cost Avoided"
            value="₹60,000"
            description="Based on current recommendations"
          />

        </div>

      </section>

    </>
  );
}


/* FLEET PAGE */

function FleetPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const filteredMachines = machines.filter((machine) => {

    const matchesSearch =
      machine.id.toLowerCase().includes(search.toLowerCase()) ||
      machine.type.toLowerCase().includes(search.toLowerCase()) ||
      machine.site.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "All" ||
      machine.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <>

      <div className="welcome">

        <div>

          <h2>Fleet</h2>

          <p>
            Monitor and manage equipment across your operating sites.
          </p>

          <div className="fleet-summary">
            <span>5 Machines</span>
            <span>3 Sites</span>
            <span>Fleet utilization 78%</span>
          </div>

        </div>

        <button className="refresh-button">
          + Add Machine
        </button>

      </div>


      <div className="fleet-toolbar">

        <input
          className="search-input"
          type="text"
          placeholder="Search machine, type or site..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <select
          className="filter-select"
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value)
          }
        >
          <option value="All">All Status</option>
          <option value="Active">Active</option>
          <option value="Idle">Idle</option>
          <option value="Alert">Alert</option>
        </select>

      </div>


      <div className="fleet-table">

        <table>

          <thead>

            <tr>
              <th>Machine</th>
              <th>Status</th>
              <th>Site</th>
              <th>Operator</th>
              <th>Utilization</th>
              <th>Idle</th>
              <th>Fuel</th>
              <th>Rental</th>
            </tr>

          </thead>


          <tbody>

            {filteredMachines.map((machine) => {

              const utilization =
                parseInt(machine.utilization);

              return (
                <tr key={machine.id}>

                  <td>
                    <div className="machine-id">
                      {machine.id}
                    </div>

                    <div className="machine-type">
                      {machine.type}
                    </div>
                  </td>


                  <td>

                    <span
                      className={`status-badge ${
                        machine.status === "Active"
                          ? "status-active"
                          : machine.status === "Idle"
                          ? "status-idle"
                          : "status-alert"
                      }`}
                    >
                      {machine.status}
                    </span>

                  </td>


                  <td>{machine.site}</td>

                  <td>{machine.operator}</td>


                  <td className="utilization-cell">

                    {machine.utilization}

                    <div className="mini-progress">

                      <div
                        className="mini-progress-fill"
                        style={{
                          width: `${utilization}%`,
                        }}
                      ></div>

                    </div>

                  </td>


                  <td>{machine.idle}</td>

                  <td>{machine.fuel}</td>

                  <td>{machine.rental}</td>

                </tr>
              );

            })}

          </tbody>

        </table>

      </div>

    </>
  );
}


/* ALERT COMPONENT */

function AlertItem({ alert }) {

  const lineClass =
    alert.severity === "HIGH"
      ? "high-line"
      : alert.severity === "MEDIUM"
      ? "medium-line"
      : "low-line";

  const textClass =
    alert.severity === "HIGH"
      ? "high"
      : alert.severity === "MEDIUM"
      ? "medium"
      : "low";

  return (
    <div className="alert">

      <div
        className={`alert-line ${lineClass}`}
      ></div>


      <div>

        <div>

          <span className={`severity ${textClass}`}>
            {alert.severity}
          </span>

          <span className="alert-time">
            {alert.time}
          </span>

        </div>


        <h3 className="alert-machine">
          {alert.machine}
        </h3>

        <p className="alert-title">
          {alert.title}
        </p>

        <p className="alert-description">
          {alert.description}
        </p>

      </div>


      <div className="alert-data">

        <span>
          Idle Time
        </span>

        <strong>
          {alert.idle}
        </strong>

      </div>


      <div className="alert-data">

        <span>
          Operator
        </span>

        <strong>
          {alert.operator}
        </strong>

      </div>


      <button className="outline-button">
        Investigate →
      </button>

    </div>
  );
}

function RentalsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const filteredRentals = rentals.filter((rental) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      rental.id.toLowerCase().includes(searchText) ||
      rental.machine.toLowerCase().includes(searchText) ||
      rental.type.toLowerCase().includes(searchText) ||
      rental.site.toLowerCase().includes(searchText);

    const matchesStatus =
      statusFilter === "All" ||
      rental.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const activeCount = rentals.filter(
    (rental) => rental.status === "Active"
  ).length;

  const endingCount = rentals.filter(
    (rental) => rental.status === "Ending Soon"
  ).length;

  const overdueCount = rentals.filter(
    (rental) => rental.status === "Overdue"
  ).length;

  return (
    <>
      <div className="welcome">

        <div>

          <h2>Rentals</h2>

          <p>
            Monitor rental commitments and equipment availability.
          </p>

          <div className="fleet-summary">
            <span>{activeCount} Active</span>
            <span>{endingCount} Ending Soon</span>
            <span>{overdueCount} Overdue</span>
          </div>

        </div>

        <button className="refresh-button">
          + New Rental
        </button>

      </div>


      <div className="metric-grid" style={{ marginBottom: "20px" }}>

        <Metric
          title="ACTIVE RENTALS"
          value={activeCount}
          description="Currently rented"
          icon="●"
        />

        <Metric
          title="ENDING SOON"
          value={endingCount}
          description="Require review"
          icon="!"
        />

        <Metric
          title="OVERDUE"
          value={overdueCount}
          description="Immediate action"
          icon="!"
        />

        <Metric
          title="TOTAL RENTALS"
          value={rentals.length}
          description="Current records"
          icon="▣"
        />

      </div>


      <div className="fleet-toolbar">

        <input
          className="search-input"
          type="text"
          placeholder="Search rental, machine or site..."
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
        />

        <select
          className="filter-select"
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value)
          }
        >
          <option value="All">
            All Status
          </option>

          <option value="Active">
            Active
          </option>

          <option value="Ending Soon">
            Ending Soon
          </option>

          <option value="Overdue">
            Overdue
          </option>

        </select>

      </div>


      <div className="fleet-table">

        <table>

          <thead>

            <tr>
              <th>Rental</th>
              <th>Machine</th>
              <th>Site</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>
              <th>Daily Rate</th>
            </tr>

          </thead>


          <tbody>

            {filteredRentals.length > 0 ? (

              filteredRentals.map((rental) => (

                <tr key={rental.id}>

                  <td>
                    <strong>
                      {rental.id}
                    </strong>
                  </td>

                  <td>
                    <div className="machine-id">
                      {rental.machine}
                    </div>

                    <div className="machine-type">
                      {rental.type}
                    </div>
                  </td>

                  <td>
                    {rental.site}
                  </td>

                  <td>
                    {rental.start}
                  </td>

                  <td>
                    {rental.end}
                  </td>

                  <td>

                    <span
                      className={`status-badge ${
                        rental.status === "Active"
                          ? "status-active"
                          : rental.status === "Ending Soon"
                          ? "status-idle"
                          : "status-alert"
                      }`}
                    >
                      {rental.status}
                    </span>

                  </td>

                  <td>
                    <strong>
                      {rental.dailyRate}
                    </strong>
                  </td>

                </tr>

              ))

            ) : (

              <tr>

                <td
                  colSpan="7"
                  style={{
                    textAlign: "center",
                    padding: "30px",
                    color: "#8b9399",
                  }}
                >
                  No rentals found.
                </td>

              </tr>

            )}

          </tbody>

        </table>

      </div>

    </>
  );
}
/* TELEMETRY PAGE */

function TelemetryPage() {
  return (
    <>

      <div className="welcome">

        <div>

          <h2>Live Telemetry</h2>

          <p>
            Current equipment operating data.
          </p>

        </div>

        <span className="updated">
          ● Live · Updated 5 sec ago
        </span>

      </div>


      <div className="fleet-table">

        <table>

          <thead>

            <tr>
              <th>Machine</th>
              <th>Engine Hours</th>
              <th>Idle Hours</th>
              <th>Fuel</th>
              <th>Engine</th>
              <th>Temperature</th>
              <th>Site</th>
            </tr>

          </thead>


          <tbody>

            {telemetry.map((item) => (
              <tr key={item.machine}>

                <td>
                  <strong>
                    {item.machine}
                  </strong>
                </td>

                <td>{item.engine}</td>
                <td>{item.idle}</td>
                <td>{item.fuel}</td>
                <td>{item.status}</td>
                <td>{item.temperature}</td>
                <td>{item.site}</td>

              </tr>
            ))}

          </tbody>

        </table>

      </div>

    </>
  );
}


/* ALERT PAGE */

function AlertsPage() {
  return (
    <>

      <div className="welcome">

        <div>

          <h2>Alert Center</h2>

          <p>
            Review and investigate fleet issues.
          </p>

        </div>

      </div>


      <div className="alert-list">

        {alerts.map((alert) => (
          <AlertItem
            key={alert.id}
            alert={alert}
          />
        ))}

      </div>

    </>
  );
}


/* RECOMMENDATIONS PAGE */

function RecommendationsPage() {
  return (
    <>

      <div className="welcome">

        <div>

          <h2>AI Decision Center</h2>

          <p>
            Review explainable recommendations and expected impact.
          </p>

        </div>

      </div>


      <div className="recommendations">

        {recommendations.map((item) => (
          <div
            className="recommendation"
            key={item.machine}
          >

            <div className="recommendation-machine">
              {item.machine}
            </div>

            <h3>
              {item.action}
            </h3>

            <p>
              {item.reason}
            </p>

            <div className="recommendation-bottom">

              <div className="impact">

                <span>
                  EXPECTED IMPACT
                </span>

                <strong>
                  {item.impact}
                </strong>

              </div>

              <div className="savings">

                <span>
                  ESTIMATED SAVING
                </span>

                <strong>
                  {item.savings}
                </strong>

              </div>

            </div>

          </div>
        ))}

      </div>

    </>
  );
}


/* PLACEHOLDER */

function PlaceholderPage({ title }) {
  return (
    <div className="page-placeholder">

      <h2>{title}</h2>

      <p>
        This module will be implemented next.
      </p>

    </div>
  );
}


/* METRIC */

function Metric({
  title,
  value,
  description,
  icon,
}) {
  return (
    <div className="metric">

      <div className="metric-top">

        <span className="metric-title">
          {title}
        </span>

        <span className="metric-icon">
          {icon}
        </span>

      </div>

      <strong className="metric-value">
        {value}
      </strong>

      <p className="metric-description">
        {description}
      </p>

    </div>
  );
}


/* BUSINESS CARD */

function BusinessCard({
  title,
  value,
  description,
}) {
  return (
    <div className="business-card">

      <span>
        {title}
      </span>

      <strong>
        {value}
      </strong>

      <small>
        {description}
      </small>

    </div>
  );
}

export default App;