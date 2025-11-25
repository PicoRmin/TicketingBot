export type AppError = {
  id: number;
  message: string;
  status?: number;
  timestamp: number;
};

type Listener = (error: AppError) => void;

let counter = 0;
const listeners = new Set<Listener>();

export function emitError(message: string, status?: number) {
  const payload: AppError = {
    id: ++counter,
    message,
    status,
    timestamp: Date.now(),
  };
  listeners.forEach((listener) => listener(payload));
}

export function subscribe(listener: Listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

