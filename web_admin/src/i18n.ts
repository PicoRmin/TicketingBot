import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import fa from "./locales/fa.json";
import en from "./locales/en.json";

const resources = {
  fa: { translation: fa },
  en: { translation: en },
};

i18n.use(initReactI18next).init({
  resources,
  lng: localStorage.getItem("imehr_lang") || "fa",
  fallbackLng: "fa",
  interpolation: {
    escapeValue: false,
  },
  detection: {
    order: ["localStorage", "navigator"],
  },
});

i18n.on("languageChanged", (lng) => {
  localStorage.setItem("imehr_lang", lng);
  document.documentElement.dir = lng === "fa" ? "rtl" : "ltr";
});

// تنظیم اولیه جهت سازگاری RTL
document.documentElement.dir = i18n.language === "fa" ? "rtl" : "ltr";

export default i18n;

