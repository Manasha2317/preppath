import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Hexagon, ArrowRight, Loader2 } from "lucide-react";
import client from "../api/client";

export default function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // Backend login expects JSON at /auth/login
      const res = await client.post("/auth/login", { email, password });
      localStorage.setItem("preppath_token", res.data.access_token);
      localStorage.setItem("preppath_user", JSON.stringify(res.data.user));
      nav("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center px-6 relative overflow-hidden">
      {/* Ambient gradient orbs */}
      <div className="absolute w-[500px] h-[500px] rounded-full blur-[120px] opacity-20 -top-40 -left-20"
           style={{ background: "radial-gradient(circle, #8b7cf8, transparent)" }} />
      <div className="absolute w-[400px] h-[400px] rounded-full blur-[120px] opacity-15 bottom-0 right-0"
           style={{ background: "radial-gradient(circle, #c9a84c, transparent)" }} />

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <Link to="/" className="flex items-center justify-center gap-2 mb-8">
          <Hexagon size={26} className="text-white" strokeWidth={1.5} />
          <span className="text-white font-semibold text-xl">PrepPath</span>
        </Link>

        <div className="liquid-glass rounded-3xl p-8">
          <h1 className="font-serif-display text-3xl text-white mb-2 text-center">Welcome back</h1>
          <p className="text-white/50 text-sm text-center mb-8">Sign in to continue your prep journey</p>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div>
              <label className="text-white/60 text-xs mb-1.5 block">Email</label>
              <input
                type="email" required value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@college.edu"
                className="w-full liquid-glass rounded-xl px-4 py-3 text-white text-sm placeholder-white/30 outline-none"
              />
            </div>
            <div>
              <label className="text-white/60 text-xs mb-1.5 block">Password</label>
              <input
                type="password" required value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full liquid-glass rounded-xl px-4 py-3 text-white text-sm placeholder-white/30 outline-none"
              />
            </div>
            <button
              type="submit" disabled={loading}
              className="mt-2 liquid-glass rounded-xl px-6 py-3 text-white text-sm font-medium flex items-center justify-center gap-2 hover:scale-[0.99] transition disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <>Sign in <ArrowRight size={16} /></>}
            </button>
          </form>

          <p className="text-white/50 text-sm text-center mt-6">
            New here?{" "}
            <Link to="/register" className="text-white hover:underline">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}