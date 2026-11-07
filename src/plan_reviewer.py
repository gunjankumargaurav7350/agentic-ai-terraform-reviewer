import json
from typing import Dict, Any, List

class PlanReviewer:
    """Analyzes Terraform Plan JSON, calculates blast radius, and detects high-risk actions."""

    RISKY_ATTRIBUTES = {
        "network_security_rule": ["0.0.0.0/0", "*"],
        "storage_account": ["public_network_access_enabled"],
        "key_vault": ["public_network_access_enabled"]
    }

    def __init__(self, plan_data: Dict[str, Any]):
        self.plan = plan_data
        self.changes = self.plan.get("resource_changes", [])

    def analyze(self) -> Dict[str, Any]:
        blast_radius = {
            "create": 0,
            "update": 0,
            "delete": 0,
            "replace": 0,
            "no_op": 0
        }
        critical_findings: List[Dict[str, str]] = []

        for change in self.changes:
            actions = change.get("change", {}).get("actions", [])
            res_type = change.get("type", "unknown")
            res_name = change.get("name", "unknown")
            res_addr = change.get("address", f"{res_type}.{res_name}")

            if actions == ["create"]:
                blast_radius["create"] += 1
            elif actions == ["update"]:
                blast_radius["update"] += 1
            elif actions == ["delete"]:
                blast_radius["delete"] += 1
                critical_findings.append({
                    "severity": "CRITICAL",
                    "resource": res_addr,
                    "issue": f"Destructive action: Resource {res_addr} will be permanently deleted."
                })
            elif "delete" in actions and "create" in actions:
                blast_radius["replace"] += 1
                critical_findings.append({
                    "severity": "HIGH",
                    "resource": res_addr,
                    "issue": f"Replacement trigger: Resource {res_addr} will be destroyed and recreated."
                })
            else:
                blast_radius["no_op"] += 1

            # Check configuration security
            after = change.get("change", {}).get("after", {}) or {}
            if res_type == "azurerm_network_security_rule":
                source = str(after.get("source_address_prefix", ""))
                dest_port = str(after.get("destination_port_range", ""))
                if source in ["*", "0.0.0.0/0"] and dest_port in ["22", "3389", "*"]:
                    critical_findings.append({
                        "severity": "CRITICAL",
                        "resource": res_addr,
                        "issue": f"Security violation: Port {dest_port} open to {source} (inbound Internet access)."
                    })

        # Calculate risk score (0 - 100)
        risk_score = min(100, (blast_radius["delete"] * 35) + (blast_radius["replace"] * 25) + (len(critical_findings) * 20))
        risk_level = "CRITICAL" if risk_score >= 70 else "HIGH" if risk_score >= 40 else "MEDIUM" if risk_score >= 15 else "LOW"

        return {
            "blast_radius": blast_radius,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "critical_findings": critical_findings,
            "requires_human_approval": risk_level in ["CRITICAL", "HIGH"] or blast_radius["delete"] > 0
        }
