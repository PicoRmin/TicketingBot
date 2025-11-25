/**
 * کامپوننت رندر فیلدهای سفارشی
 * Custom Field Renderer Component
 * 
 * این کامپوننت فیلدهای سفارشی را بر اساس نوعشان رندر می‌کند.
 * This component renders custom fields based on their type.
 */

import React from "react";

// نوع داده فیلد سفارشی با مقدار
type CustomFieldWithValue = {
  id: number;
  name: string;
  label: string;
  label_en?: string | null;
  field_type: string;
  description?: string | null;
  config?: any;
  is_required: boolean;
  is_visible_to_user: boolean;
  is_editable_by_user: boolean;
  default_value?: string | null;
  help_text?: string | null;
  placeholder?: string | null;
  value?: string | null;
  value_id?: number | null;
};

// Props کامپوننت
type CustomFieldRendererProps = {
  field: CustomFieldWithValue;
  value: string | null | undefined;
  onChange: (value: string | null) => void;
  disabled?: boolean;
  readOnly?: boolean;
};

/**
 * کامپوننت رندر فیلدهای سفارشی
 * Renders a custom field based on its type
 */
export default function CustomFieldRenderer({
  field,
  value,
  onChange,
  disabled = false,
  readOnly = false,
}: CustomFieldRendererProps) {
  // اگر فیلد قابل مشاهده نباشد، چیزی رندر نکن
  if (!field.is_visible_to_user) {
    return null;
  }

  // اگر فقط خواندنی باشد، مقدار را نمایش بده
  if (readOnly) {
    return (
      <div style={{ marginBottom: "15px" }}>
        <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
          {field.label}
          {field.is_required && <span style={{ color: "red" }}> *</span>}
        </label>
        <div style={{ padding: "8px", background: "var(--bg-secondary)", borderRadius: "6px" }}>
          {renderReadOnlyValue(field, value)}
        </div>
        {field.help_text && (
          <small style={{ color: "var(--fg-secondary)", display: "block", marginTop: "4px" }}>
            {field.help_text}
          </small>
        )}
      </div>
    );
  }

  // رندر فیلد قابل ویرایش
  return (
    <div style={{ marginBottom: "15px" }}>
      <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
        {field.label}
        {field.is_required && <span style={{ color: "red" }}> *</span>}
      </label>

      {field.description && (
        <p style={{ fontSize: "12px", color: "var(--fg-secondary)", marginBottom: "5px" }}>
          {field.description}
        </p>
      )}

      {renderFieldInput(field, value, onChange, disabled)}

      {field.help_text && (
        <small style={{ color: "var(--fg-secondary)", display: "block", marginTop: "4px" }}>
          {field.help_text}
        </small>
      )}
    </div>
  );
}

/**
 * رندر فیلد ورودی بر اساس نوع
 * Render input field based on type
 */
function renderFieldInput(
  field: CustomFieldWithValue,
  value: string | null | undefined,
  onChange: (value: string | null) => void,
  disabled: boolean
) {
  const currentValue = value || field.default_value || "";

  switch (field.field_type) {
    case "text":
    case "url":
    case "email":
    case "phone":
      return (
        <input
          type={field.field_type === "email" ? "email" : field.field_type === "url" ? "url" : "text"}
          value={currentValue}
          onChange={(e) => onChange(e.target.value || null)}
          placeholder={field.placeholder || ""}
          required={field.is_required}
          disabled={disabled || !field.is_editable_by_user}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
          }}
        />
      );

    case "textarea":
      return (
        <textarea
          value={currentValue}
          onChange={(e) => onChange(e.target.value || null)}
          placeholder={field.placeholder || ""}
          required={field.is_required}
          disabled={disabled || !field.is_editable_by_user}
          rows={4}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
            resize: "vertical",
          }}
        />
      );

    case "number":
      const config = field.config || {};
      return (
        <input
          type="number"
          value={currentValue}
          onChange={(e) => onChange(e.target.value || null)}
          placeholder={field.placeholder || ""}
          required={field.is_required}
          disabled={disabled || !field.is_editable_by_user}
          min={config.min}
          max={config.max}
          step={config.step || 1}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
          }}
        />
      );

    case "date":
      return (
        <input
          type="date"
          value={currentValue ? currentValue.split("T")[0] : ""}
          onChange={(e) => onChange(e.target.value || null)}
          required={field.is_required}
          disabled={disabled || !field.is_editable_by_user}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
          }}
        />
      );

    case "datetime":
      return (
        <input
          type="datetime-local"
          value={currentValue ? currentValue.replace("Z", "").slice(0, 16) : ""}
          onChange={(e) => onChange(e.target.value ? `${e.target.value}:00Z` : null)}
          required={field.is_required}
          disabled={disabled || !field.is_editable_by_user}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
          }}
        />
      );

    case "boolean":
      return (
        <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: disabled || !field.is_editable_by_user ? "not-allowed" : "pointer" }}>
          <input
            type="checkbox"
            checked={currentValue === "true" || currentValue === "1"}
            onChange={(e) => onChange(e.target.checked ? "true" : "false")}
            disabled={disabled || !field.is_editable_by_user}
            style={{ cursor: disabled || !field.is_editable_by_user ? "not-allowed" : "pointer" }}
          />
          <span>{currentValue === "true" || currentValue === "1" ? "بله" : "خیر"}</span>
        </label>
      );

    case "select":
      const options = field.config?.options || [];
      return (
        <select
          value={currentValue}
          onChange={(e) => onChange(e.target.value || null)}
          required={field.is_required}
          disabled={disabled || !field.is_editable_by_user}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
          }}
        >
          <option value="">-- انتخاب کنید --</option>
          {options.map((opt: any, index: number) => (
            <option key={index} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      );

    case "multiselect":
      const multiOptions = field.config?.options || [];
      const selectedValues = currentValue ? currentValue.split(",") : [];
      return (
        <div>
          {multiOptions.map((opt: any, index: number) => (
            <label
              key={index}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "8px",
                cursor: disabled || !field.is_editable_by_user ? "not-allowed" : "pointer",
              }}
            >
              <input
                type="checkbox"
                checked={selectedValues.includes(opt.value)}
                onChange={(e) => {
                  let newValues = [...selectedValues];
                  if (e.target.checked) {
                    if (!newValues.includes(opt.value)) {
                      newValues.push(opt.value);
                    }
                  } else {
                    newValues = newValues.filter((v) => v !== opt.value);
                  }
                  onChange(newValues.length > 0 ? newValues.join(",") : null);
                }}
                disabled={disabled || !field.is_editable_by_user}
                style={{ cursor: disabled || !field.is_editable_by_user ? "not-allowed" : "pointer" }}
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
      );

    default:
      return (
        <input
          type="text"
          value={currentValue}
          onChange={(e) => onChange(e.target.value || null)}
          placeholder={field.placeholder || ""}
          disabled={disabled || !field.is_editable_by_user}
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: disabled || !field.is_editable_by_user ? "var(--bg-secondary)" : "var(--bg-primary)",
          }}
        />
      );
  }
}

/**
 * رندر مقدار فقط خواندنی
 * Render read-only value
 */
function renderReadOnlyValue(field: CustomFieldWithValue, value: string | null | undefined) {
  const displayValue = value || field.default_value || "-";

  switch (field.field_type) {
    case "boolean":
      return <span>{displayValue === "true" || displayValue === "1" ? "✅ بله" : "❌ خیر"}</span>;

    case "multiselect":
      const options = field.config?.options || [];
      const selectedValues = displayValue ? displayValue.split(",") : [];
      const selectedLabels = selectedValues
        .map((val) => options.find((opt: any) => opt.value === val)?.label)
        .filter(Boolean);
      return <span>{selectedLabels.length > 0 ? selectedLabels.join(", ") : "-"}</span>;

    case "select":
      const selectOptions = field.config?.options || [];
      const selectedOption = selectOptions.find((opt: any) => opt.value === displayValue);
      return <span>{selectedOption ? selectedOption.label : displayValue}</span>;

    case "date":
      return <span>{displayValue ? new Date(displayValue).toLocaleDateString("fa-IR") : "-"}</span>;

    case "datetime":
      return (
        <span>
          {displayValue
            ? new Date(displayValue).toLocaleString("fa-IR", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit",
              })
            : "-"}
        </span>
      );

    case "url":
      return (
        <a href={displayValue} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)" }}>
          {displayValue}
        </a>
      );

    case "email":
      return (
        <a href={`mailto:${displayValue}`} style={{ color: "var(--accent)" }}>
          {displayValue}
        </a>
      );

    case "phone":
      return (
        <a href={`tel:${displayValue}`} style={{ color: "var(--accent)" }}>
          {displayValue}
        </a>
      );

    default:
      return <span>{displayValue}</span>;
  }
}

