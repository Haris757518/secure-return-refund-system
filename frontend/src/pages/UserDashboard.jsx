import { useEffect, useState } from "react";
import { fetchMyReturns, logoutUser } from "../services/api";
import ReturnForm from "../components/ReturnForm";
import ReturnCard from "../components/ReturnCard";
import {
  Shield,
  LogOut,
  FileText,
  CheckCircle,
  AlertCircle
} from "lucide-react";

export default function UserDashboard({ user, onLogout }) {
  const [returns, setReturns] = useState([]);
  const [activeTab, setActiveTab] = useState("requests");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  // ✅ User check (CORRECT place)
  if (!user) {
    return <div className="p-6 text-center">Loading...</div>;
  }

  const loadReturns = async () => {
    try {
      const data = await fetchMyReturns();
      setReturns(data);
    } catch (err) {
      setError("Failed to load returns");
    }
  };

  useEffect(() => {
    loadReturns();
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    onLogout();
  };

  const handleSuccess = (message) => {
    setSuccess(message);
    setTimeout(() => setSuccess(""), 3000);
    loadReturns();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-indigo-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <Shield className="w-8 h-8 mr-3" />
            <div>
              <h1 className="text-xl font-bold">
                Secure Return & Refund System
              </h1>
              <p className="text-sm text-indigo-200">
                {user.name || user.username} (User)
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center bg-indigo-700 hover:bg-indigo-800 px-4 py-2 rounded-lg transition"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            {success}
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" />
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex">
              <button
                onClick={() => setActiveTab("requests")}
                className={`px-6 py-3 font-medium ${
                  activeTab === "requests"
                    ? "border-b-2 border-indigo-600 text-indigo-600"
                    : "text-gray-600 hover:text-gray-800"
                }`}
              >
                My Requests
              </button>
              <button
                onClick={() => setActiveTab("submit")}
                className={`px-6 py-3 font-medium ${
                  activeTab === "submit"
                    ? "border-b-2 border-indigo-600 text-indigo-600"
                    : "text-gray-600 hover:text-gray-800"
                }`}
              >
                Submit Request
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === "submit" && (
              <ReturnForm onSuccess={handleSuccess} />
            )}

            {activeTab === "requests" && (
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  My Return Requests
                </h2>

                {returns.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p>No return requests found</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {returns.map((r) => (
                      <ReturnCard key={r._id} data={r} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
