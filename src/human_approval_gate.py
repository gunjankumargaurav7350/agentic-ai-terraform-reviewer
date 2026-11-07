from typing import Dict, Any

class HumanApprovalGate:
    """Formats markdown reports and enforces human signoff for destructive actions."""

    @staticmethod
    def generate_pr_comment(analysis: Dict[str, Any]) -> str:
        blast = analysis["blast_radius"]
        level = analysis["risk_level"]
        score = analysis["risk_score"]
        requires_approval = analysis["requires_human_approval"]

        badge_color = "red" if level == "CRITICAL" else "orange" if level == "HIGH" else "green"

        md = []
        md.append("## 🤖 Agentic AI Terraform Reviewer Briefing")
        md.append(f"**Risk Level:** `{level}` (Score: `{score}/100`) | **Action Required:** `{'⚠️ MANUAL APPROVAL MANDATORY' if requires_approval else '✅ SAFE FOR AUTO-APPLY'}`\n")
        
        md.append("### 📊 Blast Radius Summary")
        md.append("| Action | Count | Status |")
        md.append("|---|---|---|")
        md.append(f"| ➕ Resources to Create | `{blast['create']}` | Provision |")
        md.append(f"| 🔄 Resources to Update | `{blast['update']}` | In-place |")
        md.append(f"| 🔁 Resources to Replace | `{blast['replace']}` | {'⚠️ Destroy & Recreate' if blast['replace'] > 0 else 'None'} |")
        md.append(f"| ❌ Resources to Destroy | `{blast['delete']}` | {'🚨 DESTRUCTIVE' if blast['delete'] > 0 else 'None'} |\n")

        if analysis["critical_findings"]:
            md.append("### 🚨 Security & Operational Warnings")
            for item in analysis["critical_findings"]:
                md.append(f"- **[{item['severity']}]** `{item['resource']}`: {item['issue']}")
            md.append("")

        if requires_approval:
            md.append("### 🛑 Human Approval Gate")
            md.append("This plan involves destructive actions or high-severity policy concerns. Production deployment is blocked until authorized:\n")
            md.append("- [ ] **Verified Blast Radius** (No unapproved data destruction)")
            md.append("- [ ] **Security Review Signoff** (Complies with Zero Trust & CIS Benchmark)")
            md.append("- [ ] **Lead Cloud Architect Approval** (@gunjankumargaurav7350)\n")
            md.append("> *Reply `/approve` or check the boxes above to trigger production apply.*")
        else:
            md.append("### ✅ Safe for Automated Delivery")
            md.append("No destructive replacements or critical security violations detected.")

        return "\n".join(md)
