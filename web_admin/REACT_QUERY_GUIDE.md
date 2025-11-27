# راهنمای استفاده از React Query

این پروژه از **React Query (TanStack Query)** برای مدیریت state و caching استفاده می‌کند.

## 📦 نصب

```bash
npm install
```

این دستور تمام dependencies از جمله `@tanstack/react-query` و `@tanstack/react-query-devtools` را نصب می‌کند.

## 🚀 راه‌اندازی

React Query به صورت خودکار در `main.tsx` راه‌اندازی شده است:

```tsx
<QueryProvider>
  <App />
</QueryProvider>
```

## 🎯 استفاده از Custom Hooks

### useApiQuery - برای GET requests

```tsx
import { useApiQuery } from "../hooks/useApiQuery";

// مثال ساده
const { data, isLoading, error } = useApiQuery<Ticket[]>({
  endpoint: "/api/tickets",
  queryKey: ["tickets"],
});

// با فیلتر
const { data } = useApiQuery<Ticket[]>({
  endpoint: `/api/tickets?status=${status}`,
  queryKey: ["tickets", status],
});

// با refetch interval (polling)
const { data } = useApiQuery<Notification[]>({
  endpoint: "/api/notifications",
  queryKey: ["notifications"],
  refetchInterval: 60000, // هر 60 ثانیه
});
```

### useApiMutation - برای POST/PATCH/PUT/DELETE

```tsx
import { useApiMutation } from "../hooks/useApiMutation";

// مثال: ایجاد تیکت
const { mutate, isPending } = useApiMutation<Ticket, CreateTicketData>({
  method: "POST",
  endpoint: "/api/tickets",
  invalidateQueries: [["tickets"]], // بعد از موفقیت، tickets را invalidate کن
});

// استفاده
mutate({ title: "New Ticket", description: "..." });

// با dynamic endpoint
const { mutate } = useApiMutation<Ticket, { id: number; status: string }>({
  method: "PATCH",
  endpoint: (vars) => `/api/tickets/${vars.id}/status`,
  invalidateQueries: [
    ["tickets"],
    (vars) => ["tickets", vars.id], // dynamic query key
  ],
});
```

## 🔄 Query Invalidation

بعد از mutations، queries را invalidate کنید تا داده‌ها به‌روزرسانی شوند:

```tsx
import { useQueryClient } from "@tanstack/react-query";

const queryClient = useQueryClient();

// Invalidate تمام queries با key "tickets"
queryClient.invalidateQueries({ queryKey: ["tickets"] });

// Invalidate یک query خاص
queryClient.invalidateQueries({ queryKey: ["tickets", ticketId] });
```

## 🎨 React Query DevTools

در development mode، React Query DevTools به صورت خودکار فعال است:

- **Position**: bottom-right
- **Toggle**: کلیک روی دکمه در گوشه صفحه
- **Features**: مشاهده queries، mutations، cache state

## ⚙️ پیکربندی QueryClient

پیکربندی در `src/lib/queryClient.ts`:

### Default Options

- **Retry**: 3 بار برای queries، 1 بار برای mutations
- **Stale Time**: 30 ثانیه
- **Cache Time**: 5 دقیقه
- **Refetch on Window Focus**: فقط در development
- **Refetch on Reconnect**: بله

### Error Handling

- خطاهای 401/403: retry نمی‌شوند
- خطاهای دیگر: retry با exponential backoff
- خطاها از طریق `errorBus` نمایش داده می‌شوند

## 📝 مثال‌های کامل

### مثال 1: لیست تیکت‌ها

```tsx
import { useApiQuery } from "../hooks/useApiQuery";

function TicketsList() {
  const { data: tickets, isLoading, error } = useApiQuery<Ticket[]>({
    endpoint: "/api/tickets",
    queryKey: ["tickets"],
  });

  if (isLoading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error.message}</div>;

  return (
    <div>
      {tickets?.map((ticket) => (
        <div key={ticket.id}>{ticket.title}</div>
      ))}
    </div>
  );
}
```

### مثال 2: ایجاد تیکت

```tsx
import { useApiMutation } from "../hooks/useApiMutation";
import { useNavigate } from "react-router-dom";

function CreateTicket() {
  const navigate = useNavigate();
  const { mutate, isPending } = useApiMutation<Ticket, CreateTicketData>({
    method: "POST",
    endpoint: "/api/tickets",
    invalidateQueries: [["tickets"]],
    onSuccess: (data) => {
      navigate(`/tickets/${data.id}`);
    },
  });

  const handleSubmit = (formData: CreateTicketData) => {
    mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button disabled={isPending}>
        {isPending ? "در حال ایجاد..." : "ایجاد تیکت"}
      </button>
    </form>
  );
}
```

### مثال 3: به‌روزرسانی تیکت

```tsx
import { useApiMutation, useApiQuery } from "../hooks/useApiQuery";

function EditTicket({ ticketId }: { ticketId: number }) {
  // Fetch ticket
  const { data: ticket, isLoading } = useApiQuery<Ticket>({
    endpoint: `/api/tickets/${ticketId}`,
    queryKey: ["tickets", ticketId],
  });

  // Update mutation
  const { mutate, isPending } = useApiMutation<Ticket, UpdateTicketData>({
    method: "PATCH",
    endpoint: `/api/tickets/${ticketId}`,
    invalidateQueries: [
      ["tickets"],
      ["tickets", ticketId],
    ],
  });

  // ...
}
```

## 🔍 Best Practices

### 1. Query Keys

از query keys منسجم استفاده کنید:

```tsx
// ✅ خوب
["tickets"]
["tickets", ticketId]
["tickets", { status: "open" }]

// ❌ بد
["ticket-list"]
["ticket", id]
```

### 2. Invalidation

بعد از mutations، queries مرتبط را invalidate کنید:

```tsx
// ✅ خوب
invalidateQueries: [["tickets"], ["dashboard"]]

// ❌ بد
// هیچ invalidation نیست
```

### 3. Error Handling

از error handling یکپارچه استفاده کنید:

```tsx
// ✅ خوب - error از طریق errorBus نمایش داده می‌شود
const { error } = useApiQuery({ ... });

// ❌ بد - error handling دستی
try {
  await apiGet("/api/tickets");
} catch (err) {
  // ...
}
```

### 4. Loading States

از loading states استفاده کنید:

```tsx
// ✅ خوب
const { data, isLoading } = useApiQuery({ ... });
if (isLoading) return <Loading />;

// ❌ بد
const [loading, setLoading] = useState(false);
```

## 🎯 Migration از fetch مستقیم

### قبل (با fetch):

```tsx
const [tickets, setTickets] = useState([]);
const [loading, setLoading] = useState(false);

useEffect(() => {
  setLoading(true);
  apiGet("/api/tickets")
    .then(setTickets)
    .finally(() => setLoading(false));
}, []);
```

### بعد (با React Query):

```tsx
const { data: tickets, isLoading } = useApiQuery<Ticket[]>({
  endpoint: "/api/tickets",
  queryKey: ["tickets"],
});
```

## 📚 منابع بیشتر

- [React Query Documentation](https://tanstack.com/query/latest)
- [React Query DevTools](https://tanstack.com/query/latest/docs/react/devtools/devtools)
- [Query Invalidation](https://tanstack.com/query/latest/docs/react/guides/query-invalidation)

