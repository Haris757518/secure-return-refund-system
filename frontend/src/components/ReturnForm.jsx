import { useState } from "react";
import { submitReturn } from "../services/api";
import { AlertCircle, AlertTriangle } from "lucide-react";

export default function ReturnForm({ onSuccess }) {
  const [orderId, setOrderId] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!orderId || !reason || reason.length < 10) {
      setError("Please fill in all required fields correctly");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await submitReturn({ order_id: orderId, reason });
      setOrderId("");
      setReason("");
      onSuccess("Return request submitted successfully!");
    } catch (err) {
      setError(err.message || "Failed to submit return request");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Submit New Return Request</h2>
      
      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-start">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      <div className="p-3 bg-blue-50 border border-blue-200 rounded flex items-start">
        <AlertTriangle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5 text-blue-600" />
        <div className="text-sm text-blue-800">
          <p className="font-semibold mb-1">Important Notes:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>You can only submit one return per order</li>
            <li>Maximum 5 returns allowed per 24 hours</li>
            <li>Provide detailed reason for faster processing</li>
          </ul>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Order ID <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={orderId}
          onChange={(e) => setOrderId(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="Enter order ID (e.g., ORD-12345)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Reason for Return <span className="text-red-500">*</span>
        </label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="Describe the reason for your return (minimum 10 characters)..."
        />
        <p className={`text-xs mt-1 ${reason.length < 10 ? 'text-red-500' : 'text-gray-500'}`}>
          {reason.length}/10 characters minimum
        </p>
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || reason.length < 10 || !orderId}
        className="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? "Submitting..." : "Submit Return Request"}
      </button>
    </div>
  );
}