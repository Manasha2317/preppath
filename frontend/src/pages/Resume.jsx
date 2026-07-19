import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Hexagon, LayoutDashboard, FileText, MessageCircle, Target,
  LogOut, Upload, Loader2, CheckCircle2, XCircle, Sparkles, ArrowRight
} from "lucide-react";
import client from "../api/client";

function useCountUp(target, duration = 1200) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (target == null) return;
    let start = 0;
    const step = target / (duration / 16);
    const t = setInterval(() => {
      start = Math.min(start + step, target);
      setVal(start);
      if (start >= target) clearInterval(t);
    }, 16);
    return () => clearInterval(t);
  }, [target, duration]);
  return val;
}

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: FileText, label: "Resume", path: "/resume" },
  { icon: MessageCircle, label: "AI Mentor", path: "/chat" },
  { icon: Target, label: "Readiness", path: "/dashboard" },
];

export default function Resume() {
  const nav = useNavigate();
  const fileRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [phase, setPhase] = useState("idle"); // idle | uploading | processing | done | error
  const [analysis, setAnalysis] = useState(null);
  const [errMsg, setErrMsg] = useState("");

  const animatedScore = useCountUp(phase === "done" ? analysis?.ats_score : null);

  // Load latest analysis on mount (if any)
  useEffect(() => {
    client.get("/resume/latest")
      .then((res) => { setAnalysis(res.data); setPhase("done"); })
      .catch(() => {}); // no resume yet — stay idle
  }, []);

  const pollStatus = (jobId) => {
    const timer = setInterval(async () => {
      try {
        const res = await client.get(`/resume/status/${jobId}`);
        if (res.data.status === "complete") {
          clearInterval(timer);
          const latest = await client.get("/resume/latest");
          setAnalysis(latest.data);
          setPhase("done");
        } else if (res.data.status === "failed") {
          clearInterval(timer);
          setErrMsg(res.data.error_message || "Analysis failed");
          setPhase("error");
        }
      } catch {
        clearInterval(timer);
        setErrMsg("Something went wrong");
        setPhase("error");
      }
    }, 2000);
  };

  const handleFile = async (file) => {
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
      setErrMsg("Please upload a PDF file");
      setPhase("error");
      return;
    }
    setPhase("uploading");
    setErrMsg("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await client.post("/resume/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setPhase("processing");
      pollStatus(res.data.job_id);
    } catch (err) {
      setErrMsg(err.response?.data?.detail || "Upload failed");
      setPhase("error");
    }
  };

  const logout = () => {
    localStorage.removeItem("preppath_token");
    localStorage.removeItem("preppath_user");
    nav("/login");
  };

  const scoreColor = (s) => s >= 75 ? "#34d399" : s >= 50 ? "#fbbf24" : "#f87171";

  return (
    <div className="dash-bg min-h-screen flex">
      <div className="fixed w-[500px] h-[500px] rounded-full blur-[140px] opacity-[0.12] -top-40 left-40 pointer-events-none"
           style={{ background: "radial-gradient(circle, #8b7cf8, transparent)" }} />

      {/* Sidebar */}
      <aside className="w-56 shrink-0 p-4 relative z-10">
        <Link to="/" className="flex items-center gap-2 px-3 py-4 mb-4">
          <Hexagon size={22} className="text-white" strokeWidth={1.5} />
          <span className="text-white font-semibold text-lg">PrepPath</span>
        </Link>
        <nav className="flex flex-col gap-1">
          {navItems.map((item, i) => (
            <Link key={i} to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
                item.label === "Resume" ? "liquid-glass text-white" : "text-white/50 hover:text-white hover:bg-white/5"
              }`}>
              <item.icon size={18} />{item.label}
            </Link>
          ))}
        </nav>
        <button onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-white/40 hover:text-white/80 transition mt-8">
          <LogOut size={18} />Sign out
        </button>
      </aside>

      {/* Main */}
      <main className="flex-1 p-8 relative z-10 overflow-y-auto">
        <h1 className="font-serif-display text-3xl text-white mb-1">Resume Intelligence</h1>
        <p className="text-white/50 text-sm mb-8">Upload your resume to score it against your target company</p>

        {/* Upload zone */}
        {(phase === "idle" || phase === "error") && (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
            onClick={() => fileRef.current?.click()}
            className={`glass-card rounded-2xl p-16 flex flex-col items-center justify-center cursor-pointer transition ${dragging ? "border-violet-400/40 scale-[0.99]" : ""}`}
          >
            <div className="w-16 h-16 rounded-2xl liquid-glass flex items-center justify-center mb-4">
              <Upload size={26} className="text-white/70" />
            </div>
            <p className="text-white text-lg mb-1">Drop your resume here</p>
            <p className="text-white/40 text-sm">or click to browse · PDF only · max 10MB</p>
            <input ref={fileRef} type="file" accept=".pdf" hidden
              onChange={(e) => handleFile(e.target.files[0])} />
            {phase === "error" && (
              <div className="mt-4 flex items-center gap-2 text-red-300 text-sm">
                <XCircle size={16} />{errMsg}
              </div>
            )}
          </div>
        )}

        {/* Uploading / processing */}
        {(phase === "uploading" || phase === "processing") && (
          <div className="glass-card rounded-2xl p-16 flex flex-col items-center justify-center">
            <Loader2 size={32} className="text-violet-400 animate-spin mb-4" />
            <p className="text-white text-lg mb-1">
              {phase === "uploading" ? "Uploading..." : "Analyzing your resume"}
            </p>
            <p className="text-white/40 text-sm">
              {phase === "processing" ? "Extracting skills · scoring ATS · finding gaps" : "Almost there"}
            </p>
          </div>
        )}

        {/* Results */}
        {phase === "done" && analysis && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Score card */}
            <div className="glass-card rounded-2xl p-6 flex flex-col items-center justify-center">
              <div className="relative w-36 h-36 mb-4">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
                  <circle cx="60" cy="60" r="52" fill="none" stroke={scoreColor(analysis.ats_score)} strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={2 * Math.PI * 52}
                    strokeDashoffset={(2 * Math.PI * 52) - (animatedScore / 100) * (2 * Math.PI * 52)}
                    style={{ transition: "stroke-dashoffset 0.1s linear" }} />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-semibold text-white">{Math.round(animatedScore)}</span>
                  <span className="text-[10px] uppercase tracking-wider text-white/40">ATS Score</span>
                </div>
              </div>
              <p className="text-white/50 text-xs text-center">{analysis.filename}</p>
              <button onClick={() => { setPhase("idle"); setAnalysis(null); }}
                className="liquid-glass rounded-full px-4 py-2 text-white text-xs mt-4">
                Upload another
              </button>
            </div>

            {/* Breakdown */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-white/40 text-xs uppercase tracking-wider mb-4">Score Breakdown</p>
              {[
                ["Sections", analysis.breakdown.section_score, 20],
                ["Keywords", analysis.breakdown.keyword_score, 30],
                ["Metrics", analysis.breakdown.metrics_score, 20],
                ["Length", analysis.breakdown.length_score, 10],
                ["Action Verbs", analysis.breakdown.action_verb_score, 10],
                ["Contact", analysis.breakdown.contact_score, 10],
              ].map(([label, val, max], i) => (
                <div key={i} className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-white/60">{label}</span>
                    <span className="text-white/80">{val}/{max}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/6 overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-1000"
                      style={{ width: `${(val / max) * 100}%`, background: val / max >= 0.7 ? "#34d399" : val / max >= 0.4 ? "#fbbf24" : "#f87171" }} />
                  </div>
                </div>
              ))}
            </div>

            {/* Skills + suggestions */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Missing for target</p>
              <div className="flex flex-wrap gap-2 mb-5">
                {(analysis.missing_keywords || []).map((k, i) => (
                  <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300">{k}</span>
                ))}
              </div>
              <p className="text-white/40 text-xs uppercase tracking-wider mb-3">Top Suggestions</p>
              <div className="flex flex-col gap-2">
                {(analysis.suggestions || []).slice(0, 3).map((s, i) => (
                  <div key={i} className="flex gap-2 text-xs text-white/60 leading-snug">
                    <Sparkles size={12} className="text-violet-400 shrink-0 mt-0.5" />{s}
                  </div>
                ))}
              </div>
              <Link to="/chat"
                className="liquid-glass rounded-xl px-4 py-2.5 text-white text-sm flex items-center justify-center gap-2 mt-5 hover:scale-[0.99] transition">
                Discuss with AI Mentor <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}