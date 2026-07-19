import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Hexagon, LayoutDashboard, FileText, MessageCircle, Target,
  LogOut, TrendingUp, TrendingDown, Sparkles, Upload, ArrowRight, Loader2
} from "lucide-react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer
} from "recharts";
import client from "../api/client";

// Animated count-up hook
function useCountUp(target, duration = 1200) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (target == null) return;
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start = Math.min(start + step, target);
      setVal(start);
      if (start >= target) clearInterval(timer);
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return val;
}

function ReadinessRing({ value }) {
  const animated = useCountUp(value);
  const circumference = 2 * Math.PI * 52;
  const offset = circumference - (animated / 100) * circumference;
  return (
    <div className="relative w-40 h-40">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle
          cx="60" cy="60" r="52" fill="none" stroke="url(#ringGrad)" strokeWidth="8"
          strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.1s linear" }}
        />
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a78bfa" />
            <stop offset="50%" stopColor="#60a5fa" />
            <stop offset="100%" stopColor="#c9a84c" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-semibold text-white">{Math.round(animated)}%</span>
        <span className="text-[10px] uppercase tracking-wider text-white/40">Ready</span>
      </div>
    </div>
  );
}

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: FileText, label: "Resume", path: "/resume" },
  { icon: MessageCircle, label: "AI Mentor", path: "/chat" },
  { icon: Target, label: "Readiness", path: "/dashboard" },
];

export default function Dashboard() {
  const nav = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const resumeScore = useCountUp(data?.resume_score);
  const skillsFound = useCountUp(data?.skills_found);

  useEffect(() => {
    client.get("/dashboard")
      .then((res) => setData(res.data))
      .catch(() => setError("Could not load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  const logout = () => {
    localStorage.removeItem("preppath_token");
    localStorage.removeItem("preppath_user");
    nav("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center">
        <Loader2 size={28} className="text-white/50 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center text-white/60">
        {error}
      </div>
    );
  }

  const radarData = (data.skill_radar || []).map((s) => ({ axis: s.axis, value: s.value }));

  return (
    <div className="dash-bg min-h-screen flex">
      {/* Ambient orbs */}
      <div className="fixed w-[500px] h-[500px] rounded-full blur-[140px] opacity-[0.12] -top-40 left-40 pointer-events-none"
           style={{ background: "radial-gradient(circle, #8b7cf8, transparent)" }} />
      <div className="fixed w-[400px] h-[400px] rounded-full blur-[140px] opacity-[0.08] bottom-0 right-20 pointer-events-none"
           style={{ background: "radial-gradient(circle, #c9a84c, transparent)" }} />

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
                item.label === "Dashboard"
                  ? "liquid-glass text-white"
                  : "text-white/50 hover:text-white hover:bg-white/5"
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
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-serif-display text-3xl text-white">
              Hi {data.student_name?.split(" ")[0]} 👋
            </h1>
            <p className="text-white/50 text-sm mt-1">
              Targeting <span className="text-white/80">{data.target_company}</span> · {data.readiness_status}
            </p>
          </div>
          <Link to="/resume"
            className="liquid-glass rounded-full px-5 py-2.5 text-white text-sm flex items-center gap-2 hover:scale-95 transition">
            <Upload size={16} />Upload Resume
          </Link>
        </div>

        {/* Top row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          {/* Readiness */}
          <div className="glass-card rounded-2xl p-6 flex items-center gap-6">
            <ReadinessRing value={data.overall_readiness} />
            <div>
              <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Overall Readiness</p>
              <p className="text-white text-lg font-medium mb-2">{data.readiness_status}</p>
              <p className="text-white/50 text-xs leading-relaxed">
                Close your skill gaps to reach the next tier for {data.target_company}.
              </p>
            </div>
          </div>

          {/* Resume score */}
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-2 text-white/40 text-xs uppercase tracking-wider mb-3">
              <FileText size={14} /> Resume Score
            </div>
            <div className="text-4xl font-semibold text-white mb-1">
              {data.resume_score != null ? Math.round(resumeScore) : "—"}
              <span className="text-lg text-white/30">/100</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-emerald-400">
              <TrendingUp size={12} /> ATS optimized
            </div>
          </div>

          {/* Skills / gaps */}
          <div className="glass-card rounded-2xl p-6">
            <div className="flex items-center gap-2 text-white/40 text-xs uppercase tracking-wider mb-3">
              <Sparkles size={14} /> Skills Snapshot
            </div>
            <div className="flex items-end gap-6">
              <div>
                <div className="text-4xl font-semibold text-white">{Math.round(skillsFound)}</div>
                <div className="text-xs text-white/40">skills found</div>
              </div>
              <div>
                <div className="text-4xl font-semibold text-amber-400">{data.gaps_remaining}</div>
                <div className="text-xs text-white/40">gaps remaining</div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Radar */}
          <div className="glass-card rounded-2xl p-6">
            <p className="text-white/40 text-xs uppercase tracking-wider mb-4">Skill Radar</p>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="axis" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }} />
                <Radar dataKey="value" stroke="#8b7cf8" fill="#8b7cf8" fillOpacity={0.25} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Priority actions */}
          <div className="glass-card rounded-2xl p-6">
            <p className="text-white/40 text-xs uppercase tracking-wider mb-4">AI Priority Actions</p>
            <div className="flex flex-col gap-3">
              {(data.priority_actions || []).map((a) => (
                <div key={a.rank} className="flex gap-3">
                  <div className="w-6 h-6 rounded-lg liquid-glass flex items-center justify-center text-xs text-white shrink-0 mt-0.5">
                    {a.rank}
                  </div>
                  <div>
                    <p className="text-white text-sm leading-snug">{a.action}</p>
                    <p className="text-white/40 text-xs mt-0.5">{a.reason} · {a.impact}</p>
                  </div>
                </div>
              ))}
            </div>
            <Link to="/chat"
              className="liquid-glass rounded-xl px-4 py-2.5 text-white text-sm flex items-center justify-center gap-2 mt-4 hover:scale-[0.99] transition">
              Ask your AI Mentor <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}