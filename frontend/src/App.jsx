import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";

function Placeholder({ name }) {
  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff" }}>
      {name} — coming soon
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Placeholder name="Login" />} />
        <Route path="/register" element={<Placeholder name="Register" />} />
        <Route path="/dashboard" element={<Placeholder name="Dashboard" />} />
        <Route path="/resume" element={<Placeholder name="Resume" />} />
        <Route path="/chat" element={<Placeholder name="Chat" />} />
      </Routes>
    </BrowserRouter>
  );
}