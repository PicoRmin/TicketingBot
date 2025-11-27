import { FormEvent, useEffect, useMemo, useReducer, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import gsap from "gsap";
import { apiPost } from "../services/api";

type IdentitySection = {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
};

type OrganizationSection = {
  branch: string;
  department: string;
  jobTitle: string;
  employeeCode: string;
};

type SecuritySection = {
  username: string;
  password: string;
  confirmPassword: string;
  otpTarget: string;
  otpCode: string;
};

type ConsentSection = {
  acceptTerms: boolean;
  shareInsights: boolean;
};

type RegisterFormState = {
  identity: IdentitySection;
  organization: OrganizationSection;
  security: SecuritySection;
  consent: ConsentSection;
};

type RegisterAction =
  | { type: "identity"; payload: Partial<IdentitySection> }
  | { type: "organization"; payload: Partial<OrganizationSection> }
  | { type: "security"; payload: Partial<SecuritySection> }
  | { type: "consent"; payload: Partial<ConsentSection> }
  | { type: "reset" };

const initialState: RegisterFormState = {
  identity: {
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
  },
  organization: {
    branch: "",
    department: "",
    jobTitle: "",
    employeeCode: "",
  },
  security: {
    username: "",
    password: "",
    confirmPassword: "",
    otpTarget: "",
    otpCode: "",
  },
  consent: {
    acceptTerms: false,
    shareInsights: true,
  },
};

const reducer = (state: RegisterFormState, action: RegisterAction): RegisterFormState => {
  switch (action.type) {
    case "identity":
      return { ...state, identity: { ...state.identity, ...action.payload } };
    case "organization":
      return { ...state, organization: { ...state.organization, ...action.payload } };
    case "security":
      return { ...state, security: { ...state.security, ...action.payload } };
    case "consent":
      return { ...state, consent: { ...state.consent, ...action.payload } };
    case "reset":
      return initialState;
    default:
      return state;
  }
};

type StepId = "identity" | "organization" | "security" | "review";

type StepDefinition = {
  id: StepId;
  title: string;
  description: string;
};

export default function Register() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [state, dispatch] = useReducer(reducer, initialState);
  const [step, setStep] = useState<StepId>("identity");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [otpStatus, setOtpStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [serverMessage, setServerMessage] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const steps: StepDefinition[] = useMemo(
    () => [
      {
        id: "identity",
        title: t("auth.register.steps.identity.title"),
        description: t("auth.register.steps.identity.description"),
      },
      {
        id: "organization",
        title: t("auth.register.steps.organization.title"),
        description: t("auth.register.steps.organization.description"),
      },
      {
        id: "security",
        title: t("auth.register.steps.security.title"),
        description: t("auth.register.steps.security.description"),
      },
      {
        id: "review",
        title: t("auth.register.steps.review.title"),
        description: t("auth.register.steps.review.description"),
      },
    ],
    [t]
  );

  useEffect(() => {
    if (!panelRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        panelRef.current,
        { autoAlpha: 0, y: 24 },
        { autoAlpha: 1, y: 0, duration: 0.45, ease: "power3.out" }
      );
    }, panelRef);
    return () => ctx.revert();
  }, [step]);

  const currentStepIndex = steps.findIndex((cfg) => cfg.id === step);
  const primaryCtaLabel = step === "review" ? t("auth.register.actions.submit") : t("auth.register.actions.next");

  const setStepByIndex = (index: number) => {
    const next = steps[Math.min(Math.max(index, 0), steps.length - 1)];
    setStep(next.id);
  };

  const validateStep = (stepId: StepId) => {
    const nextErrors: Record<string, string> = {};
    if (stepId === "identity") {
      if (!state.identity.firstName.trim()) {
        nextErrors["identity.firstName"] = t("auth.register.validation.required");
      }
      if (!state.identity.lastName.trim()) {
        nextErrors["identity.lastName"] = t("auth.register.validation.required");
      }
      if (!state.identity.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        nextErrors["identity.email"] = t("auth.register.validation.email");
      }
      if (state.identity.phone.trim().length < 10) {
        nextErrors["identity.phone"] = t("auth.register.validation.phone");
      }
    }
    if (stepId === "organization") {
      if (!state.organization.branch.trim()) {
        nextErrors["organization.branch"] = t("auth.register.validation.required");
      }
      if (!state.organization.department.trim()) {
        nextErrors["organization.department"] = t("auth.register.validation.required");
      }
    }
    if (stepId === "security") {
      if (!state.security.username.trim()) {
        nextErrors["security.username"] = t("auth.register.validation.required");
      }
      if (state.security.password.length < 6) {
        nextErrors["security.password"] = t("auth.register.validation.password");
      }
      if (state.security.password !== state.security.confirmPassword) {
        nextErrors["security.confirmPassword"] = t("auth.register.validation.passwordMatch");
      }
      if (!state.security.otpTarget.match(/@|^\d{10,}$/)) {
        nextErrors["security.otpTarget"] = t("auth.register.validation.otpTarget");
      }
      if (!state.security.otpCode.trim()) {
        nextErrors["security.otpCode"] = t("auth.register.validation.required");
      }
    }
    if (stepId === "review" && !state.consent.acceptTerms) {
      nextErrors["consent.acceptTerms"] = t("auth.register.validation.terms");
    }

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep(step)) return;
    setStepByIndex(currentStepIndex + 1);
  };

  const handlePrev = () => {
    setErrors({});
    setStepByIndex(currentStepIndex - 1);
  };

  const handleSendOtp = async () => {
    if (!state.security.otpTarget) {
      setErrors((prev) => ({ ...prev, "security.otpTarget": t("auth.register.validation.otpTarget") }));
      return;
    }
    setOtpStatus("sending");
    try {
      await apiPost("/api/auth/register/otp", {
        target: state.security.otpTarget,
      });
      setOtpStatus("sent");
      setServerMessage(t("auth.register.messages.otpSent"));
    } catch (err) {
      console.warn("OTP request failed:", err);
      setOtpStatus("error");
      setServerMessage(t("auth.register.messages.otpError"));
    } finally {
      setTimeout(() => setOtpStatus("idle"), 2500);
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!validateStep("review")) return;
    setSubmitting(true);
    setServerMessage(null);
    try {
      await apiPost("/api/auth/register", {
        identity: state.identity,
        organization: state.organization,
        security: {
          username: state.security.username,
          password: state.security.password,
          otp_code: state.security.otpCode,
        },
        consent: state.consent,
      });
      setCompleted(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : t("auth.register.messages.genericError");
      setServerMessage(message);
    } finally {
      setSubmitting(false);
    }
  };

  if (completed) {
    return (
      <div className="register-page gradient-bg">
        <motion.div
          className="register-card success"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, ease: "backOut" }}
        >
          <h1>{t("auth.register.success.title")}</h1>
          <p>{t("auth.register.success.subtitle")}</p>
          <Link to="/login" className="button primary">
            {t("auth.register.success.cta")}
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="register-page gradient-bg">
      <div className="register-card">
        <header className="register-header">
          <div>
            <p className="register-eyebrow">{t("auth.register.eyebrow")}</p>
            <h1>{t("auth.register.title")}</h1>
            <p className="register-subtitle">{t("auth.register.subtitle")}</p>
          </div>
          <div className="register-progress">
            {steps.map((cfg, index) => (
              <button
                key={cfg.id}
                type="button"
                className={`register-progress__item ${cfg.id === step ? "active" : ""} ${
                  index < currentStepIndex ? "complete" : ""
                }`}
                onClick={() => {
                  if (index <= currentStepIndex) {
                    setStep(cfg.id);
                  }
                }}
              >
                <span>{index + 1}</span>
                <small>{cfg.title}</small>
              </button>
            ))}
          </div>
        </header>

        <form className="register-form" onSubmit={handleSubmit}>
          <motion.div
            key={step}
            ref={panelRef}
            className="register-panel"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.35 }}
          >
            <h2>{steps[currentStepIndex].title}</h2>
            <p className="register-panel__subtitle">{steps[currentStepIndex].description}</p>

            {step === "identity" && (
              <div className="register-grid">
                <label>
                  {t("auth.register.fields.firstName")}
                  <input
                    value={state.identity.firstName}
                    onChange={(e) => dispatch({ type: "identity", payload: { firstName: e.target.value } })}
                    aria-invalid={Boolean(errors["identity.firstName"])}
                  />
                  {errors["identity.firstName"] && <span className="form-error">{errors["identity.firstName"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.lastName")}
                  <input
                    value={state.identity.lastName}
                    onChange={(e) => dispatch({ type: "identity", payload: { lastName: e.target.value } })}
                    aria-invalid={Boolean(errors["identity.lastName"])}
                  />
                  {errors["identity.lastName"] && <span className="form-error">{errors["identity.lastName"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.email")}
                  <input
                    type="email"
                    value={state.identity.email}
                    onChange={(e) => dispatch({ type: "identity", payload: { email: e.target.value } })}
                    aria-invalid={Boolean(errors["identity.email"])}
                  />
                  {errors["identity.email"] && <span className="form-error">{errors["identity.email"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.phone")}
                  <input
                    value={state.identity.phone}
                    onChange={(e) => dispatch({ type: "identity", payload: { phone: e.target.value } })}
                    aria-invalid={Boolean(errors["identity.phone"])}
                  />
                  {errors["identity.phone"] && <span className="form-error">{errors["identity.phone"]}</span>}
                </label>
              </div>
            )}

            {step === "organization" && (
              <div className="register-grid">
                <label>
                  {t("auth.register.fields.branch")}
                  <input
                    value={state.organization.branch}
                    onChange={(e) => dispatch({ type: "organization", payload: { branch: e.target.value } })}
                    aria-invalid={Boolean(errors["organization.branch"])}
                    placeholder={t("auth.register.placeholders.branch")}
                  />
                  {errors["organization.branch"] && <span className="form-error">{errors["organization.branch"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.department")}
                  <input
                    value={state.organization.department}
                    onChange={(e) => dispatch({ type: "organization", payload: { department: e.target.value } })}
                    aria-invalid={Boolean(errors["organization.department"])}
                    placeholder={t("auth.register.placeholders.department")}
                  />
                  {errors["organization.department"] && (
                    <span className="form-error">{errors["organization.department"]}</span>
                  )}
                </label>
                <label>
                  {t("auth.register.fields.jobTitle")}
                  <input
                    value={state.organization.jobTitle}
                    onChange={(e) => dispatch({ type: "organization", payload: { jobTitle: e.target.value } })}
                    placeholder={t("auth.register.placeholders.jobTitle")}
                  />
                </label>
                <label>
                  {t("auth.register.fields.employeeCode")}
                  <input
                    value={state.organization.employeeCode}
                    onChange={(e) => dispatch({ type: "organization", payload: { employeeCode: e.target.value } })}
                    placeholder="BR-92-IT"
                  />
                </label>
              </div>
            )}

            {step === "security" && (
              <div className="register-grid">
                <label>
                  {t("auth.register.fields.username")}
                  <input
                    value={state.security.username}
                    onChange={(e) => dispatch({ type: "security", payload: { username: e.target.value } })}
                    aria-invalid={Boolean(errors["security.username"])}
                  />
                  {errors["security.username"] && <span className="form-error">{errors["security.username"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.password")}
                  <input
                    type="password"
                    value={state.security.password}
                    onChange={(e) => dispatch({ type: "security", payload: { password: e.target.value } })}
                    aria-invalid={Boolean(errors["security.password"])}
                  />
                  {errors["security.password"] && <span className="form-error">{errors["security.password"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.confirmPassword")}
                  <input
                    type="password"
                    value={state.security.confirmPassword}
                    onChange={(e) => dispatch({ type: "security", payload: { confirmPassword: e.target.value } })}
                    aria-invalid={Boolean(errors["security.confirmPassword"])}
                  />
                  {errors["security.confirmPassword"] && (
                    <span className="form-error">{errors["security.confirmPassword"]}</span>
                  )}
                </label>
                <label className="otp-field">
                  {t("auth.register.fields.otpTarget")}
                  <div className="otp-input">
                    <input
                      value={state.security.otpTarget}
                      onChange={(e) => dispatch({ type: "security", payload: { otpTarget: e.target.value } })}
                      aria-invalid={Boolean(errors["security.otpTarget"])}
                      placeholder="user@example.com"
                    />
                    <button type="button" onClick={handleSendOtp} disabled={otpStatus === "sending"}>
                      {otpStatus === "sending" ? t("auth.register.actions.sendingOtp") : t("auth.register.actions.sendOtp")}
                    </button>
                  </div>
                  {errors["security.otpTarget"] && <span className="form-error">{errors["security.otpTarget"]}</span>}
                </label>
                <label>
                  {t("auth.register.fields.otpCode")}
                  <input
                    value={state.security.otpCode}
                    onChange={(e) => dispatch({ type: "security", payload: { otpCode: e.target.value } })}
                    aria-invalid={Boolean(errors["security.otpCode"])}
                    placeholder="123456"
                  />
                  {errors["security.otpCode"] && <span className="form-error">{errors["security.otpCode"]}</span>}
                </label>
                {serverMessage && <div className="alert info">{serverMessage}</div>}
              </div>
            )}

            {step === "review" && (
              <div className="register-review">
                <div>
                  <h3>{t("auth.register.review.identity")}</h3>
                  <ul>
                    <li>
                      {state.identity.firstName} {state.identity.lastName}
                    </li>
                    <li>{state.identity.email}</li>
                    <li>{state.identity.phone}</li>
                  </ul>
                </div>
                <div>
                  <h3>{t("auth.register.review.organization")}</h3>
                  <ul>
                    <li>{state.organization.branch}</li>
                    <li>{state.organization.department}</li>
                    <li>{state.organization.jobTitle}</li>
                  </ul>
                </div>
                <label className="consent-checkbox">
                  <input
                    type="checkbox"
                    checked={state.consent.acceptTerms}
                    onChange={(e) => dispatch({ type: "consent", payload: { acceptTerms: e.target.checked } })}
                  />
                  <span>{t("auth.register.review.acceptTerms")}</span>
                </label>
                {errors["consent.acceptTerms"] && <span className="form-error">{errors["consent.acceptTerms"]}</span>}
                <label className="consent-checkbox">
                  <input
                    type="checkbox"
                    checked={state.consent.shareInsights}
                    onChange={(e) => dispatch({ type: "consent", payload: { shareInsights: e.target.checked } })}
                  />
                  <span>{t("auth.register.review.shareInsights")}</span>
                </label>
              </div>
            )}
          </motion.div>

          <footer className="register-actions">
            <button type="button" className="ghost" onClick={handlePrev} disabled={currentStepIndex === 0}>
              {t("auth.register.actions.prev")}
            </button>
            {step === "review" ? (
              <button type="submit" disabled={submitting}>
                {submitting ? t("auth.register.actions.submitting") : primaryCtaLabel}
              </button>
            ) : (
              <button type="button" onClick={handleNext}>
                {primaryCtaLabel}
              </button>
            )}
          </footer>
        </form>

        <div className="register-footer">
          <span>{t("auth.register.haveAccount")}</span>
          <Link to="/login">{t("auth.register.goToLogin")}</Link>
        </div>
      </div>
    </div>
  );
}


