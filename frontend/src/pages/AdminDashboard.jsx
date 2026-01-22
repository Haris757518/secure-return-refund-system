import { useEffect, useState } from "react";
import {
  fetchAllReturns,
  approveReturn,
  rejectReturn,
  completeRefund,
  logoutUser,
  fetchAuditLogs
} from "../services/api";

import {
  Shield,
  LogOut,
  CheckCircle,
  XCircle,
  Clock,
  FileText
} from "lucide-react";

export default function AdminDashboard({ user, onLogout }) {
  const [returns, setReturns] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [activeTab, setActiveTab] = useState("returns");
  const [message, setMessage] = useState("");

  const loadData = async () => {
    setReturns(await fetchAllReturns());
    setAuditLogs(await fetchAuditLogs());
  };

  useEffect(() => {
    loadData();
  }, []);

  const statusBadge = (status) => {
    if (status === "Pending") return "bg-yellow-100 text-yellow-800";
    if (status === "Approved") return "bg-green-100 text-green-800";
    if (status === "Rejected") return "bg-red-100 text-red-800";
    return "bg-gray-100 text-gray-800";
  };

  const refundBadge = (status) => {
    if (status === "Refund Initiated") return "text-blue-600";
    if (status === "Refund Successful") return "text-green-600";
    return "text-gray-500";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* HEADER */}
      <div className="bg-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Shield />
            <div>
              <h1 className="text-lg font-bold">Secure Return & Refund System</h1>
              <p className="text-indigo-200 text-sm">
                {user?.username} (Administrator)
              </p>
            </div>
          </div>

          <button
            onClick={async () => {
              await logoutUser();
              onLogout();
            }}
            className="flex items-center gap-2 bg-indigo-700 px-4 py-2 rounded"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </div>

      {/* BODY */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {message && (
          <div className="mb-4 bg-green-100 text-green-700 px-4 py-2 rounded">
            {message}
          </div>
        )}

        {/* TABS */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab("returns")}
            className={`px-4 py-2 rounded ${
              activeTab === "returns"
                ? "bg-indigo-600 text-white"
                : "bg-gray-200"
            }`}
          >
            Returns
          </button>

          <button
            onClick={() => setActiveTab("audit")}
            className={`px-4 py-2 rounded ${
              activeTab === "audit"
                ? "bg-indigo-600 text-white"
                : "bg-gray-200"
            }`}
          >
            Audit Logs
          </button>
        </div>

        {/* RETURNS TAB */}
        {activeTab === "returns" && (
          <div className="space-y-4">
            {returns.length === 0 ? (
              <div className="text-center text-gray-500">
                <FileText className="mx-auto mb-2" />
                No return requests
              </div>
            ) : (
              returns.map((r) => (
                <div
                  key={r._id}
                  className="bg-white border rounded-lg p-5 shadow-sm"
                >
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold text-lg">{r.order_id}</h3>
                    <span
                      className={`px-3 py-1 text-xs rounded ${statusBadge(
                        r.status
                      )}`}
                    >
                      {r.status}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-2">{r.reason}</p>

                  <p className="text-sm">
                    <span className="font-medium">Refund Status:</span>{" "}
                    <span className={`font-semibold ${refundBadge(r.refund_status)}`}>
                      {r.refund_status || "Not Initiated"}
                    </span>
                  </p>

                  {/* ACTIONS */}
                  <div className="mt-4 flex gap-2">
                    {r.status === "Pending" && (
                      <>
                        <button
                          onClick={async () => {
                            await approveReturn(r._id);
                            setMessage("Return approved & refund initiated");
                            loadData();
                          }}
                          className="bg-green-600 text-white px-4 py-1 rounded"
                        >
                          Approve
                        </button>

                        <button
                          onClick={async () => {
                            await rejectReturn(r._id);
                            loadData();
                          }}
                          className="bg-red-600 text-white px-4 py-1 rounded"
                        >
                          Reject
                        </button>
                      </>
                    )}

                    {r.refund_status === "Refund Initiated" && (
                      <button
                        onClick={async () => {
                          await completeRefund(r._id);
                          setMessage("Refund marked as successful");
                          loadData();
                        }}
                        className="bg-blue-600 text-white px-4 py-1 rounded"
                      >
                        Complete Refund
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* AUDIT LOGS TAB */}
        {activeTab === "audit" && (
          <div className="bg-white rounded-lg shadow p-5 space-y-3">
            {auditLogs.map((log) => (
              <div key={log._id} className="border-b pb-2">
                <p className="font-semibold text-indigo-600">{log.action}</p>
                <p className="text-sm">{log.details}</p>
                <p className="text-xs text-gray-500">
                  {new Date(log.timestamp).toLocaleString()} | {log.actor}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
