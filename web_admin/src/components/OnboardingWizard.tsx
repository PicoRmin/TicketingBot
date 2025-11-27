import { useEffect, useRef, useState } from "react";
import { apiPost } from "../services/api";
import gsap from "gsap";

type OnboardingProfile = {
  firstName: string;
  lastName: string;
  phone: string;
  ageRange: string;
  skillLevel: string;
  goals: string[];
  responsibilities: string;
  notes: string;
};

const ONBOARDING_KEY = "imehr_onboarding_state";
const GOAL_LIBRARY = ["بهبود مهارت شبکه", "مدیریت شعب", "حل سریع مشکلات", "یادگیری نرم‌افزارهای جدید"];

const defaultProfile: OnboardingProfile = {
  firstName: "",
  lastName: "",
  phone: "",
  ageRange: "",
  skillLevel: "",
  goals: [],
  responsibilities: "",
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
  const steps = ["اطلاعات پایه", "اهداف و مسئولیت‌ها", "بازبینی و تایید"];
  const tooltipContent: Record<number, { title: string; hints: string[]; highlight: "panel" | "chips" | "review" }> = {
    0: {
      title: "راهنمای تکمیل اطلاعات پایه",
      hints: ["نام و نام خانوادگی رسمی را درج کنید.", "شماره تماس قابل دسترس روزانه را بنویسید.", "رده سنی و سطح مهارت، پیشنهادهای بعدی را دقیق‌تر می‌کند."],
      highlight: "panel",
    },
    1: {
      title: "اهداف و مسئولیت‌ها",
      hints: ["حداقل دو هدف شغلی انتخاب کنید.", "شرح مسئولیت‌ها باعث سفارشی‌سازی اعلان‌ها می‌شود.", "می‌توانید هدف جدید تایپ و با Enter اضافه کنید."],
      highlight: "chips",
    },
    2: {
      title: "بازبینی و تایید نهایی",
      hints: ["اطلاعات شخصی و اهداف را یک‌بار مرور کنید.", "در صورت نیاز می‌توانید به مراحل قبل بازگردید.", "با تایید نهایی، تنظیمات در پروفایل ذخیره می‌شود."],
      highlight: "review",
    },
  };
  const tooltipRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem(ONBOARDING_KEY, JSON.stringify(state));
  }, [state]);

  useEffect(() => {
    if (!tooltipRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        tooltipRef.current,
        { autoAlpha: 0, y: 12 },
        { autoAlpha: 1, y: 0, duration: 0.4, ease: "power2.out" }
      );
    }, tooltipRef);
    return () => ctx.revert();
  }, [state.step]);

  const updateProfile = (changes: Partial<OnboardingProfile>) => {
    setState((prev) => ({
      ...prev,
      profile: { ...prev.profile, ...changes },
    }));
  };

  const toggleGoal = (value: string) => {
    setState((prev) => {
      const current = prev.profile.goals;
      const exists = current.includes(value);
      const updated = exists ? current.filter((item) => item !== value) : [...current, value];
      return {
        ...prev,
        profile: {
          ...prev.profile,
          goals: updated,
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
        <div className="onboarding-panel highlight-ring">
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
          <div className="chip-list highlight-ring">
            {GOAL_LIBRARY.map((goal) => (
              <button
                type="button"
                key={goal}
                className={`chip ${profile.goals.includes(goal) ? "active" : ""}`}
                onClick={() => toggleGoal(goal)}
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
          <label>
          یادداشت‌های تکمیلی:
            <textarea
              rows={3}
              value={profile.notes}
              onChange={(e) => updateProfile({ notes: e.target.value })}
              placeholder="هر نکته‌ای که به تیم پشتیبانی کمک می‌کند را وارد کنید."
            />
          </label>
        </div>
      )}

      {state.step === 2 && (
        <div className="onboarding-panel highlight-ring">
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
            {profile.notes && (
            <li>
                <strong>توضیحات:</strong> {profile.notes}
            </li>
            )}
          </ul>
        </div>
      )}

      {tooltipContent[state.step] && (
        <div className="onboarding-tooltip" ref={tooltipRef}>
          <h4>{tooltipContent[state.step].title}</h4>
          <ul>
            {tooltipContent[state.step].hints.map((hint) => (
              <li key={hint}>{hint}</li>
            ))}
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

