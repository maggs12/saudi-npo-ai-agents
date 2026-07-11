"use client";

import { useEffect, useState } from "react";

interface DashboardData {
  programs: Array<{
    name: string;
    status: string;
    overall_progress: number;
  }>;
  volunteers: {
    total_volunteers: number;
    open_opportunities: number;
  };
  finance: {
    total_income: number;
    total_expenses: number;
    balance: number;
  };
}

interface Message {
  role: "user" | "ai";
  content: string;
}

export default function Home() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", content: "أهلاً بك! كيف يمكنني مساعدتك اليوم؟" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const apiKey = process.env.NEXT_PUBLIC_API_KEY || "";
  const headers: Record<string, string> = apiKey ? { "X-API-Key": apiKey } : {};

  useEffect(() => {
    fetch("/api/v1/dashboard?organization_id=1", { headers })
      .then((res) => res.json())
      .then((data) => setDashboard(data))
      .catch(() => setDashboard(null));
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch("/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...headers },
        body: JSON.stringify({ message: userMessage }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "ai", content: data.response || "تم تنفيذ طلبك." }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "ai", content: "حدث خطأ في الاتصال بالخادم." }]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    "إنشاء برنامج جديد",
    "تسجيل متطوع جديد",
    "توليد تقرير PDF",
    "فحص الامتثال",
    "ملخص المالية",
  ];

  return (
    <main className="min-h-screen p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-primary">منصة وكلاء الذكاء الاصطناعي للقطاع غير الربحي</h1>
        <p className="text-slate-600 mt-2">لوحة تحكم موحدة للبرامج والتطوع والحوكمة والتقارير</p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-surface rounded-xl shadow p-5">
          <h2 className="text-sm text-slate-500">إجمالي الإيرادات</h2>
          <p className="text-2xl font-bold text-accent">
            {dashboard?.finance?.total_income?.toLocaleString() ?? "--"} ريال
          </p>
        </div>
        <div className="bg-surface rounded-xl shadow p-5">
          <h2 className="text-sm text-slate-500">إجمالي المصروفات</h2>
          <p className="text-2xl font-bold text-danger">
            {dashboard?.finance?.total_expenses?.toLocaleString() ?? "--"} ريال
          </p>
        </div>
        <div className="bg-surface rounded-xl shadow p-5">
          <h2 className="text-sm text-slate-500">الرصيد</h2>
          <p className="text-2xl font-bold text-primary">
            {dashboard?.finance?.balance?.toLocaleString() ?? "--"} ريال
          </p>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-surface rounded-xl shadow p-5">
          <h2 className="text-sm text-slate-500">المتطوعين</h2>
          <p className="text-2xl font-bold text-primary">{dashboard?.volunteers?.total_volunteers ?? "--"}</p>
        </div>
        <div className="bg-surface rounded-xl shadow p-5">
          <h2 className="text-sm text-slate-500">فرص التطوع المفتوحة</h2>
          <p className="text-2xl font-bold text-secondary">{dashboard?.volunteers?.open_opportunities ?? "--"}</p>
        </div>
        <div className="bg-surface rounded-xl shadow p-5">
          <h2 className="text-sm text-slate-500">البرامج</h2>
          <p className="text-2xl font-bold text-primary">{dashboard?.programs?.length ?? "--"}</p>
        </div>
      </section>

      {dashboard && dashboard.programs.length > 0 && (
        <section className="bg-surface rounded-xl shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-primary mb-4">حالة البرامج</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-right">
              <thead className="border-b">
                <tr>
                  <th className="py-2">اسم البرنامج</th>
                  <th className="py-2">الحالة</th>
                  <th className="py-2">التقدم الكلي</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.programs.map((p, idx) => (
                  <tr key={idx} className="border-b last:border-0">
                    <td className="py-2">{p.name}</td>
                    <td className="py-2">{p.status}</td>
                    <td className="py-2">{p.overall_progress}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="bg-surface rounded-xl shadow p-6">
        <h2 className="text-xl font-bold text-primary mb-4">المساعد الذكي</h2>
        <div className="flex flex-wrap gap-2 mb-4">
          {quickActions.map((action) => (
            <button
              key={action}
              onClick={() => setInput(action)}
              className="px-3 py-1 text-sm bg-slate-100 hover:bg-slate-200 rounded-full text-slate-700"
            >
              {action}
            </button>
          ))}
        </div>
        <div className="h-80 overflow-y-auto border rounded-lg p-4 mb-4 bg-slate-50">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`mb-3 p-3 rounded-lg max-w-3xl ${
                m.role === "user" ? "bg-primary text-white mr-auto" : "bg-white shadow text-slate-800"
              }`}
            >
              {m.content}
            </div>
          ))}
          {loading && <div className="text-slate-500">جاري التفكير...</div>}
        </div>
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="اكتب رسالتك هنا..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-primary"
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50"
          >
            إرسال
          </button>
        </div>
      </section>
    </main>
  );
}
