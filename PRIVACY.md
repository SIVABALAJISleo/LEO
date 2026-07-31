# Privacy Policy — LEO AI

**Last Updated**: 2026-07-29
**Effective Date**: 2026-07-29
**Project**: LEO AI Enterprise Intelligence Platform
**Contact**: Contact the maintainer via the GitHub repository.

---

## 1. Introduction

LEO AI ("we", "our", or "the Service") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, store, and protect your information when you use LEO AI.

---

## 2. Data We Collect

### Account Data

- Email address and username (stored in the application database)
- Encrypted password hash (stored via Bcrypt — never in plain text)
- Tenant ID for multi-tenant workspace isolation

### Usage Data

- AI queries and responses (stored locally in SQLite database; never sent to third parties)
- Session activity logs (for rate limiting and abuse prevention only)
- System metric telemetry (CPU, memory usage — used only for performance optimization)

### Technical Data

- Browser type and version (for cross-browser compatibility)
- IP address (for rate limiting only — not stored permanently)
- HttpOnly session cookie (`leo.jwt`) — stored in browser, expires in 7 days

---

## 3. How We Use Your Data

- To authenticate you and manage your session securely
- To provide AI inference services and store your workspace memory
- To enforce rate limits and prevent abuse
- To improve local model accuracy (all processing is local — no data is sent to external AI APIs)
- To maintain service security and audit compliance

---

## 4. Data Sharing & Third Parties

| Third Party          | Purpose                                   | Privacy Policy                                       |
| :------------------- | :---------------------------------------- | :--------------------------------------------------- |
| **Supabase**         | Authentication & database (if configured) | [supabase.com/privacy](https://supabase.com/privacy) |
| **Railway / Render** | Hosting (if configured)                   | Per hosting provider                                 |

**We do NOT:**

- Sell your data to any third party
- Share your data for advertising or marketing
- Send your queries to external AI cloud APIs (all inference is local)

---

## 5. Your Rights

### Under GDPR (EU Users)

- **Right to Access**: Request a copy of your stored data
- **Right to Erasure**: Request deletion of your account and data
- **Right to Portability**: Request your data in a machine-readable format
- **Right to Rectification**: Request correction of inaccurate data

### Under DPDP Act 2023 (India Users)

- **Right to Correction and Erasure** of personal data
- **Right to Grievance Redressal**
- **Right to Nominate** a representative for data management

---

## 6. Data Retention

- Account data is retained until you delete your account
- Session cookies expire after 7 days
- Usage logs are retained for 30 days for security purposes

---

## 7. Security

- Passwords are hashed with Bcrypt (industry-standard)
- Sessions use HttpOnly, Secure, SameSite=Lax cookies
- All API endpoints enforce JWT authentication
- Rate limiting (60 requests/minute) prevents brute force attacks
- Content Security Policy (CSP) headers prevent XSS attacks

---

## 8. Changes to This Policy

We will notify users of material changes by updating the "Last Updated" date at the top of this document.

---

## 9. Contact

For privacy enquiries, data deletion requests, or compliance questions, please open an issue on the [GitHub repository](https://github.com/SIVABALAJISleo/LEO).
