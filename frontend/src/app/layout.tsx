import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "منصة وكلاء الذكاء الاصطناعي للقطاع غير الربحي",
  description: "منصة متعددة الوكلاء لإدارة الجمعيات والمؤسسات غير الربحية في السعودية",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className="antialiased">{children}</body>
    </html>
  );
}
