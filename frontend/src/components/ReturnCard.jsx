import { Clock, CheckCircle, XCircle } from "lucide-react";

export default function ReturnCard({ data }) {
  const getStatusIcon = (status) => {
    switch(status) {
      case 'Pending': return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'Approved': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Rejected': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return null;
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'Pending': return 'bg-yellow-100 text-yellow-800';
      case 'Approved': return 'bg-green-100 text-green-800';
      case 'Rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <span className="font-semibold text-gray-800 mr-3">
              Request ID: {data._id}
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(data.status)}`}>
              {data.status}
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-1">
            <span className="font-medium">Order ID:</span> {data.order_id}
          </p>
          <p className="text-sm text-gray-600 mb-1">
            <span className="font-medium">Submitted:</span>{" "}
            {new Date(data.created_at).toLocaleString()}
          </p>
        </div>
        {getStatusIcon(data.status)}
      </div>
      
      <div className="bg-gray-50 rounded p-3">
        <p className="text-sm font-medium text-gray-700 mb-1">Reason:</p>
        <p className="text-sm text-gray-600">{data.reason}</p>
      </div>
    </div>
  );
}