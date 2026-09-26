import type { Metadata } from "next";
import { IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

const font = IBM_Plex_Sans({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-plex",
});

export const metadata: Metadata = {
  title: "Foresight — AI Churn Prediction",
  description: "Enterprise-grade churn prediction with XGBoost, SHAP explainability, and drift monitoring.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${font.variable} h-full antialiased`}>
      <body className="min-h-full bg-slate-50 dark:bg-slate-950 font-sans">{children}</body>
    </html>
  );
}
