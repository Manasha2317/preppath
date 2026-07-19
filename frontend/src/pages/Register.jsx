import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Hexagon, ArrowRight, Loader2 } from "lucide-react";
import client from "../api/client";

export default function Register() {
  const nav = useNavigate();
  const [form, setForm] = useState({
    full_name: "", email: "", password: "",
    college: "", department: "", cgpa: "",
    graduation_year: "", target_role: "", target_company: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await client.post("/auth/register", form);
      localStorage.setItem("preppath_token", res.data.access_token);
      localStorage.setItem("preppath_user", JSON.stringify(res.data.user));
      nav("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  const field = (label, key, type = "text", placeholder = "") => (
    <div>
      <label className="text-white/60 text-xs mb-1.5 block">{label}</label>
      <input
        type={type} value={form[key]} onChange={update(key)}
        placeholder={placeholder}
        className="w-full liquid-glass rounded-xl px-4 py-2.5 text-white text-sm placeholder-white/30 outline-none"
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex items-center justify-center px-6 py-12 relative overflow-hidden">
      <div className="absolute w-[500px] h-[500px] rounded-full blur-[120px] opacity-20 -top-40 -right-20"
           style={{ background: "radial-gradient(circle, #4f8ef7, transparent)" }} />
      <div className="absolute w-[400px] h-[400px] rounded-full blur-[120px] opacity-15 bottom-0 left-0"
           style={{ background: "radial-gradient(circle, #c9a84c, transparent)" }} />

      <div className="relative z-10 w-full max-w-lg">
        <Link to="/" className="flex items-center justify-center gap-2 mb-6">
          <Hexagon size={26} className="text-white" strokeWidth={1.5} />
          <span className="text-white font-semibold text-xl">PrepPath</span>
        </Link>

        <div className="liquid-glass rounded-3xl p-8">
          <h1 className="font-serif-display text-3xl text-white mb-2 text-center">Create your account</h1>
          <p className="text-white/50 text-sm text-center mb-6">Start building your Career Digital Twin</p>

          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="flex flex-col gap-3">
            {field("Full Name", "full_name", "text", "Manasha Colekar")}
            {field("Email", "email", "email", "you@college.edu")}
            {field("Password", "password", "password", "••••••••")}
            <div className="grid grid-cols-2 gap-3">
              {field("College", "college", "text", "CIT")}
              {field("Department", "department", "text", "CSE")}
            </div>
            <div className="grid grid-cols-2 gap-3">
              {field("CGPA", "cgpa", "text", "8.0")}
              {field("Graduation Year", "graduation_year", "text", "2028")}
            </div>
            <div className="grid grid-cols-2 gap-3">
              {field("Target Role", "target_role", "text", "AI Engineer")}
              {field("Target Company", "target_company", "text", "Amazon")}
            </div>
            <button
              type="submit" disabled={loading}
              className="mt-2 liquid-glass rounded-xl px-6 py-3 text-white text-sm font-medium flex items-center justify-center gap-2 hover:scale-[0.99] transition disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <>Create account <ArrowRight size={16} /></>}
            </button>
          </form>

          <p className="text-white/50 text-sm text-center mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-white hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}