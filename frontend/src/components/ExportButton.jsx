import { Download } from "lucide-react";

export default function ExportButton({ data }) {
  const handleExport = () => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `review-report-${data.product_id || "export"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button onClick={handleExport} className="btn-secondary text-xs">
      <Download className="h-3.5 w-3.5" />
      Export JSON
    </button>
  );
}
