# Security Policy

## 🔒 Security Overview

The Claude Reflect System is designed with security and privacy as core principles:

- ✅ **100% Local** - All data stays on your machine
- ✅ **No Cloud Communication** - Zero network requests
- ✅ **Privacy First** - Your code and corrections never leave your system
- ✅ **Open Source** - Full transparency, audit the code yourself

## 🛡️ Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## 🐛 Reporting a Vulnerability

### Where to Report

**DO NOT** open public issues for security vulnerabilities.

Instead, email: **security@haddock-development.com** (or haddock.development@gmail.com)

### What to Include

Please provide:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Impact** assessment (who's affected, what's at risk)
4. **Possible fix** (if you have one)
5. **Your contact info** for follow-up

### Response Timeline

- **24-48 hours:** Initial acknowledgment
- **7 days:** Preliminary assessment
- **30 days:** Fix released (for critical issues)
- **90 days:** Public disclosure (coordinated)

### Disclosure Policy

We follow **coordinated disclosure**:

1. You report the issue privately
2. We confirm and develop a fix
3. We release a patch
4. We publicly credit you (if desired)
5. Details are disclosed after users can update

## 🔐 Security Considerations

### Data Storage

**What We Store:**
- Skill files (YAML + Markdown) in `~/.claude/skills/`
- Backups in `.backups/` directories
- Git history in `.git/` directory
- State files in `.state/` directory

**What We DON'T Store:**
- Your actual code/projects
- API keys or credentials
- Personal information
- Usage analytics

### File Permissions

Recommended permissions:
```bash
chmod 700 ~/.claude/skills/           # Owner only
chmod 600 ~/.claude/skills/*/*.md     # Owner read/write only
chmod 700 ~/.claude/skills/*/scripts/ # Owner execute only
```

### Sensitive Data

**⚠️ NEVER commit:**
- API keys
- Passwords
- Personal data
- Proprietary code
- Credentials of any kind

The system includes `.gitignore` to prevent accidental commits.

### Git Repository Risks

If you push skills to GitHub:

**Public Repos:**
- ✅ Share reflection system (safe)
- ✅ Share learned preferences (safe)
- ❌ Share company-specific skills (could leak IP)
- ❌ Share credentials (even in history)

**Private Repos:**
- ✅ Share team learnings
- ⚠️ Still avoid credentials
- ⚠️ Review before pushing

### Backup Security

**Automatic Backups:**
- Stored in `.backups/` subdirectories
- Auto-cleaned after 30 days
- Same permissions as original files

**Manual Backups:**
- Recommended: encrypt before external storage
- Use `tar + gpg` for secure backups:
  ```bash
  tar czf - ~/.claude/skills | gpg -c > skills-backup.tar.gz.gpg
  ```

## 🚨 Known Security Considerations

### 1. Arbitrary Code Execution

**Risk:** Skills can execute Python/Shell scripts
**Mitigation:**
- Only install skills from trusted sources
- Review script contents before use
- System doesn't auto-execute unknown code

### 2. YAML Parsing

**Risk:** Malicious YAML could exploit parser
**Mitigation:**
- We use `yaml.safe_load()` (not `load()`)
- Validation before processing
- Rollback on errors

### 3. Git History

**Risk:** Sensitive data in commit history
**Mitigation:**
- Review before committing
- Use `.gitignore` properly
- Git filter-branch if needed:
  ```bash
  git filter-branch --tree-filter 'rm -f sensitive_file' HEAD
  ```

### 4. Hook Execution

**Risk:** Hook scripts run automatically
**Mitigation:**
- Hooks are opt-in (disabled by default)
- User controls hook configuration
- Timeouts prevent runaway processes

### 5. Transcript Parsing

**Risk:** Large transcripts could cause memory issues
**Mitigation:**
- Line-by-line processing
- Graceful error handling
- Background processing for auto-mode

## ✅ Security Best Practices

### For Users

1. **Review Skills** before installing
2. **Check Diffs** before approving changes
3. **Use Git** for version control
4. **Backup** regularly
5. **Update** to latest version
6. **Private Repos** for team skills
7. **Encrypt Backups** if external storage

### For Developers

1. **Input Validation** on all user data
2. **Safe YAML Parsing** (`safe_load` only)
3. **File Permissions** checks
4. **Error Handling** everywhere
5. **No Eval/Exec** of user strings
6. **Path Traversal** prevention
7. **Dependency Audits** regularly

## 🔍 Security Audits

### Self-Audit Checklist

- [ ] Review all Python scripts
- [ ] Check file permissions
- [ ] Verify `.gitignore` coverage
- [ ] Test with malformed inputs
- [ ] Check for hardcoded secrets
- [ ] Validate YAML parsing
- [ ] Test rollback mechanisms

### Professional Audit

**Interested in auditing?** Contact us at security@haddock-development.com

## 📋 Security Updates

We announce security updates via:
- GitHub Security Advisories
- Release notes
- README.md updates

**Subscribe to releases:** Watch → Custom → Releases

## 🏆 Responsible Disclosure Recognition

We credit security researchers (with permission) in:
- SECURITY.md
- Release notes
- GitHub Security Advisories

**Hall of Fame:** (No reports yet - be the first!)

## ⚖️ Legal

This project:
- Is provided "AS IS" without warranty
- Has no liability for data loss
- Requires user review before changes
- Is licensed under MIT

See [LICENSE](LICENSE) for full details.

## 📞 Contact

- **Security Issues:** security@haddock-development.com
- **General Questions:** haddock.development@gmail.com
- **GitHub Issues:** https://github.com/haddock-development/claude-reflect-system/issues

---

**Security is a shared responsibility. Stay safe!** 🔒
