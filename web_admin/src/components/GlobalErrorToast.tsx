import { useEffect, useState } from "react";
import { AppError, subscribe } from "../services/errorBus";

const AUTO_HIDE_MS = 5000;

export function GlobalErrorToast() {
  const [errors, setErrors] = useState<AppError[]>([]);

  useEffect(() => {
    const unsubscribe = subscribe((error) => {
      setErrors((prev) => [...prev, error]);
      setTimeout(() => {
        setErrors((prev) => prev.filter((item) => item.id !== error.id));
      }, AUTO_HIDE_MS);
    });

    return () => unsubscribe();
  }, []);

  if (!errors.length) {
    return null;
  }

  return (
    <div className="global-error-toast">
      {errors.map((error) => (
        <div key={error.id} className="toast-item">
          <strong>⚠️</strong> {error.message}
          {error.status && <span style={{ fontSize: 12 }}> ({error.status})</span>}
        </div>
      ))}
    </div>
  );
}

