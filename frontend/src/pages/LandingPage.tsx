import { ArrowRight, Calendar, Mail, Sparkles, CheckSquare, MessageSquare, Shield } from 'lucide-react'
import React from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function LandingPage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  return (
    <div className="min-h-screen bg-white text-gray-900">

      {/* ── Nav ── */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-blue-600" />
          <span className="text-lg font-bold tracking-tight">DailyBrief</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
            Sign in
          </Link>
          <Link
            to="/signup"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition-colors"
          >
            Get started
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="max-w-4xl mx-auto px-8 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 mb-6">
          <Sparkles className="h-3 w-3" />
          AI-powered morning briefing
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 leading-tight mb-6">
          Your entire day,<br />
          <span className="text-blue-600">ready before you start it.</span>
        </h1>
        <p className="text-lg text-gray-500 max-w-xl mx-auto mb-10 leading-relaxed">
          DailyBrief pulls your emails, calendar, and tasks every morning and hands you a prioritized briefing — with an AI assistant to answer questions and take action.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 transition-colors shadow-sm"
          >
            Start for free
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 rounded-xl border border-gray-200 px-6 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Sign in
          </Link>
        </div>
      </section>

      {/* ── Feature strip ── */}
      <section className="bg-gray-50 border-y border-gray-100 py-16">
        <div className="max-w-5xl mx-auto px-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: <Mail className="h-5 w-5 text-blue-600" />,
              title: 'Inbox, classified',
              desc: 'Every email sorted into Urgent, Can Wait, or FYI — so you know exactly what needs your attention today.',
            },
            {
              icon: <Calendar className="h-5 w-5 text-green-600" />,
              title: 'Calendar, analysed',
              desc: "Conflicts, back-to-back meetings, and free slots surfaced automatically. No more surprised by a double-booking.",
            },
            {
              icon: <CheckSquare className="h-5 w-5 text-amber-600" />,
              title: 'Tasks, prioritized',
              desc: 'Notion tasks classified as Overdue, Due Today, or Due Later — with AI suggestions to slot them into free calendar time.',
            },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
              <div className="rounded-lg bg-gray-50 w-9 h-9 flex items-center justify-center mb-4">
                {f.icon}
              </div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="max-w-3xl mx-auto px-8 py-20 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">How it works</h2>
        <p className="text-gray-500 mb-12">Three steps, every morning.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          {[
            { step: '01', title: 'Connect your tools', desc: 'Link Gmail, Google Calendar, and Notion once. DailyBrief handles the rest.' },
            { step: '02', title: 'Run your briefing', desc: 'One click pulls everything together — emails, events, and tasks — into a single prioritized view.' },
            { step: '03', title: 'Chat and act', desc: 'Ask questions, draft replies, or schedule tasks — all from the built-in AI chat panel.' },
          ].map((s) => (
            <div key={s.step} className="rounded-2xl border border-gray-100 p-6">
              <p className="text-3xl font-black text-blue-100 mb-3">{s.step}</p>
              <h3 className="text-sm font-bold text-gray-900 mb-2">{s.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Chat callout ── */}
      <section className="bg-blue-600 py-16">
        <div className="max-w-3xl mx-auto px-8 flex flex-col md:flex-row items-center gap-8">
          <div className="flex-shrink-0 bg-blue-500 rounded-2xl p-5">
            <MessageSquare className="h-8 w-8 text-white" />
          </div>
          <div className="text-center md:text-left">
            <h2 className="text-2xl font-bold text-white mb-2">Built-in AI assistant</h2>
            <p className="text-blue-100 leading-relaxed">
              Ask "What's my 2pm about?", "Draft a reply to Sarah", or "Schedule the design review for 3pm" — and get instant answers from your own data.
            </p>
          </div>
        </div>
      </section>

      {/* ── Security note ── */}
      <section className="max-w-3xl mx-auto px-8 py-16 text-center">
        <Shield className="h-8 w-8 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">Your data stays yours</h2>
        <p className="text-sm text-gray-500 max-w-lg mx-auto">
          OAuth tokens are encrypted at rest per user. No email content or calendar data is stored permanently — only your briefing summaries.
        </p>
      </section>

      {/* ── CTA ── */}
      <section className="bg-gray-50 border-t border-gray-100 py-16 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to start your mornings better?</h2>
        <Link
          to="/signup"
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-8 py-3 text-sm font-semibold text-white hover:bg-blue-700 transition-colors shadow-sm"
        >
          Create your free account
          <ArrowRight className="h-4 w-4" />
        </Link>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-gray-100 px-8 py-6 flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <Sparkles className="h-3 w-3" />
          <span>DailyBrief</span>
        </div>
        <p>Built with Gemini · Gmail · Google Calendar · Notion</p>
      </footer>

    </div>
  )
}
