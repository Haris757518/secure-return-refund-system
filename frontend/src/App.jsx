import { useState } from "react";
import LoginPage from "./pages/LoginPage";
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";

export default function App() {
  const [user, setUser] = useState(null);

  if (!user) {
    return <LoginPage onLogin={setUser} />;
  }

  if (user.role === "admin") {
    return <AdminDashboard user={user} onLogout={() => setUser(null)} />;
  }

  return <UserDashboard user={user} onLogout={() => setUser(null)} />;
}
