import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";

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
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Placeholder name="Dashboard" />} />
        <Route path="/resume" element={<Placeholder name="Resume" />} />
        <Route path="/chat" element={<Placeholder name="Chat" />} />
      </Routes>
    </BrowserRouter>
  );
}