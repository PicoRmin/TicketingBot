import { useEffect, useState } from "react";
import { apiPost } from "../services/api";

type OnboardingProfile = {
  firstName: string;
  lastName: string;
  phone: string;
  ageRange: string;
  skillLevel: string;
  goals: string[];
  responsibilities: string;
  preferredHabits: string[];
  notes: string;
};

const ONBOARDING_KEY = "imehr_onboarding_state";
const HABIT_LIBRARY = ["پیگیری روزانه تیکت‌ها", "ثبت گزارش پایانی", "اشتراک دانش در بانک", "ارائه بازخورد SLA"];
const GOAL_LIBRARY = ["بهبود مهارت شبکه", "مدیریت شعب", "حل سریع مشکلات", "یادگیری نرم‌افزارهای جدید"];

const defaultProfile: OnboardingProfile = {
  firstName: "",
  lastName: "",
  phone: "",
  ageRange: "",
  skillLevel: "",
  goals: [],
  responsibilities: "",
  preferredHabits: [],
  notes: "",
};

type OnboardingState = {
  completed: boolean;
  step: number;
  profile: OnboardingProfile;
};

type Props = {
  onComplete?: () => void;
};

export function OnboardingWizard({ onComplete }: Props) {
  const [state, setState] = useState<OnboardingState>(() => {
    if (typeof window === "undefined") return { completed: false, step: 0, profile: defaultProfile };
    try {
      const raw = localStorage.getItem(ONBOARDING_KEY);
      if (raw) {
        return JSON.parse(raw) as OnboardingState;
      }
    } catch {
      /* ignore */
    }
    return { completed: false, step: 0, profile: defaultProfile };
  });
  const [saving, setSaving] = useState(false);
  const steps = [
    "اطلاعات پایه",
    "اهداف و مسئولیت‌ها",
    "عادات پیشنهادی",
    "بازبینی و تایید",
  ];

  useEffect(() => {
    localStorage.setItem(ONBOARDING_KEY, JSON.stringify(state));
  }, [state]);

  const updateProfile = (changes: Partial<OnboardingProfile>) => {
    setState((prev) => ({
      ...prev,
      profile: { ...prev.profile, ...changes },
    }));
  };

  const toggleListValue = (key: "goals" | "preferredHabits", value: string) => {
    setState((prev) => {
      const current = prev.profile[key];
      const exists = current.includes(value);
      const updated = exists ? current.filter((item) => item !== value) : [...current, value];
      return {
        ...prev,
        profile: {
          ...prev.profile,
          [key]: updated,
        },
      };
    });
  };

  const handleNext = () => {
    setState((prev) => ({
      ...prev,
      step: Math.min(prev.step + 1, steps.length - 1),
    }));
  };

  const handleBack = () => {
    setState((prev) => ({
      ...prev,
      step: Math.max(prev.step - 1, 0),
    }));
  };

  const handleSkip = () => {
    const nextState = { ...state, completed: true };
    setState(nextState);
    localStorage.setItem(ONBOARDING_KEY, JSON.stringify(nextState));
    onComplete?.();
  };

  const handleSubmit = async () => {
    setSaving(true);
    try {
      await apiPost("/api/profile/onboarding", state.profile);
    } catch (err) {
      console.warn("Onboarding submission fallback:", err);
    } finally {
      const nextState = { ...state, completed: true };
      setState(nextState);
      localStorage.setItem(ONBOARDING_KEY, JSON.stringify(nextState));
      setSaving(false);
      onComplete?.();
    }
  };

  if (state.completed) {
    return (
      <div className="onboarding-card completed">
        <div>
          <h2>🎉 اطلاعات شما تکمیل شد</h2>
          <p style={{ margin: 0, color: "var(--fg-secondary)" }}>
            می‌توانید در هر زمان از تنظیمات دوباره این فرم را بازبینی کنید.
          </p>
        </div>
        <button className="secondary" onClick={() => setState({ ...state, completed: false, step: 0 })}>
          ویرایش مجدد
        </button>
      </div>
    );
  }

  const { profile } = state;

  return (
    <div className="onboarding-card">
      <div className="onboarding-header">
        <div>
          <h2>🎯 تکمیل پروفایل هوشمند</h2>
          <p>با چند مرحله ساده تجربه شخصی‌سازی‌شده‌ای دریافت کنید.</p>
        </div>
        <button className="secondary" onClick={handleSkip}>
          بعداً انجام می‌دهم
        </button>
      </div>

      <div className="onboarding-progress">
        {steps.map((label, index) => (
          <div key={label} className={`onboarding-progress__step ${index <= state.step ? "active" : ""}`}>
            <span>{index + 1}</span>
            <small>{label}</small>
          </div>
        ))}
      </div>

      {state.step === 0 && (
        <div className="onboarding-panel">
          <label>
            نام:
            <input value={profile.firstName} onChange={(e) => updateProfile({ firstName: e.target.value })} placeholder="علی" />
          </label>
          <label>
            نام خانوادگی:
            <input value={profile.lastName} onChange={(e) => updateProfile({ lastName: e.target.value })} placeholder="احمدی" />
          </label>
          <label>
            شماره تماس:
            <input value={profile.phone} onChange={(e) => updateProfile({ phone: e.target.value })} placeholder="0912xxxxxxx" />
          </label>
          <div className="onboarding-grid">
            <label>
              رده سنی:
              <select value={profile.ageRange} onChange={(e) => updateProfile({ ageRange: e.target.value })}>
                <option value="">انتخاب کنید</option>
                <option value="18-25">18 تا 25</option>
                <option value="26-35">26 تا 35</option>
                <option value="36-45">36 تا 45</option>
                <option value="46+">بالای 45</option>
              </select>
            </label>
            <label>
              سطح مهارت IT:
              <select value={profile.skillLevel} onChange={(e) => updateProfile({ skillLevel: e.target.value })}>
                <option value="">انتخاب کنید</option>
                <option value="beginner">مبتدی</option>
                <option value="intermediate">متوسط</option>
                <option value="advanced">حرفه‌ای</option>
              </select>
            </label>
          </div>
        </div>
      )}

      {state.step === 1 && (
        <div className="onboarding-panel">
          <p>اهداف کاری خود را انتخاب یا وارد کنید:</p>
          <div className="chip-list">
            {GOAL_LIBRARY.map((goal) => (
              <button
                type="button"
                key={goal}
                className={`chip ${profile.goals.includes(goal) ? "active" : ""}`}
                onClick={() => toggleListValue("goals", goal)}
              >
                {goal}
              </button>
            ))}
          </div>
          <label>
            مسئولیت‌های اصلی:
            <textarea
              rows={3}
              value={profile.responsibilities}
              onChange={(e) => updateProfile({ responsibilities: e.target.value })}
              placeholder="مثال: پیگیری مشکلات شبکه شعب غرب، هماهنگی با تیم VOIP..."
            />
          </label>
        </div>
      )}

      {state.step === 2 && (
        <div className="onboarding-panel">
          <p>عادت‌های پیشنهادی را انتخاب کنید:</p>
          <div className="chip-list">
            {HABIT_LIBRARY.map((habit) => (
              <button
                type="button"
                key={habit}
                className={`chip ${profile.preferredHabits.includes(habit) ? "active" : ""}`}
                onClick={() => toggleListValue("preferredHabits", habit)}
              >
                {habit}
              </button>
            ))}
          </div>
          <label>
            توضیحات تکمیلی:
            <textarea
              rows={3}
              value={profile.notes}
              onChange={(e) => updateProfile({ notes: e.target.value })}
              placeholder="هر نکته‌ای که به تیم پشتیبانی کمک می‌کند را وارد کنید."
            />
          </label>
        </div>
      )}

      {state.step === 3 && (
        <div className="onboarding-panel">
          <h3>مرور اطلاعات</h3>
          <ul className="onboarding-review">
            <li>
              <strong>نام کامل:</strong> {`${profile.firstName || "-"} ${profile.lastName || ""}`}
            </li>
            <li>
              <strong>مهارت:</strong> {profile.skillLevel || "-"}
            </li>
            <li>
              <strong>اهداف:</strong> {profile.goals.length ? profile.goals.join("، ") : "-"}
            </li>
            <li>
              <strong>مسئولیت‌ها:</strong> {profile.responsibilities || "-"}
            </li>
            <li>
              <strong>عادات منتخب:</strong> {profile.preferredHabits.length ? profile.preferredHabits.join("، ") : "-"}
            </li>
          </ul>
        </div>
      )}

      <div className="onboarding-actions">
        <button className="secondary" onClick={handleBack} disabled={state.step === 0}>
          قبلی
        </button>
        {state.step < steps.length - 1 ? (
          <button onClick={handleNext}>
            مرحله بعد
          </button>
        ) : (
          <button onClick={handleSubmit} disabled={saving}>
            {saving ? "در حال ذخیره..." : "تایید و اتمام"}
          </button>
        )}
      </div>
    </div>
  );
}

