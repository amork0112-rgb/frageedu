import { useSearchParams } from "react-router-dom";
import EntranceStepper from "../components/EntranceStepper";

export default function EntrancePage() {
  const [params] = useSearchParams();
  const brchType = params.get("brchType") || "kinder";
  const flowType = params.get("flowType") || "transfer"; // kinder only
  const step = parseInt(params.get("step") || "1", 10);
  const token = params.get("id") || "";

  return <EntranceStepper brchType={brchType} flowType={flowType} step={step} token={token} />;
}