import re
from typing import Dict, Any

class CITroubleshooter:
    """Diagnoses CI/CD failures and provides exact remediation recommendations."""

    ERROR_PATTERNS = [
        {
            "id": "AZURE_QUOTA_EXCEEDED",
            "regex": r"(ResourceQuotaExceeded|Core quota exceeded|quota limit exceeded)",
            "title": "Azure Regional Core Quota Exceeded",
            "root_cause": "The subscription has reached the compute core / public IP quota limit in the selected region.",
            "remediation": "1. Request a quota increase via Azure Portal > Quotas.
2. Or shift non-critical test workloads to an alternate paired region (e.g., East US 2)."
        },
        {
            "id": "CIRCULAR_DEPENDENCY",
            "regex": r"(Cycle:|cycle in dependency graph)",
            "title": "Terraform Graph Circular Dependency",
            "root_cause": "Two or more resources reference each other directly, preventing Terraform from resolving execution order.",
            "remediation": "1. Decouple cross-resource references by using standalone association resources (e.g., azurerm_subnet_network_security_group_association).
2. Audit 'depends_on' blocks for mutual references."
        },
        {
            "id": "STATE_LOCK_TIMEOUT",
            "regex": r"(Error acquiring the state lock|blob is already leased)",
            "title": "Terraform State Locking Conflict",
            "root_cause": "A previous pipeline was cancelled without releasing the Azure Blob Lease, or another deployment is currently active.",
            "remediation": "1. Confirm no active pipeline is executing.
2. Break the lease via Azure CLI:
   az storage blob lease break --blob-name <state-key> --container-name tfstate --account-name <storage-acct>"
        },
        {
            "id": "CIDR_OVERLAP",
            "regex": r"(SubnetPrefixRangeOverlaps|Address space .* conflicts with)",
            "title": "Virtual Network CIDR Overlap Conflict",
            "root_cause": "The assigned address prefix overlaps with an existing subnet or peered VNet.",
            "remediation": "1. Run IPAM audit to find an unallocated /24 or /26 block.
2. Update the subnet CIDR variable in terraform.tfvars."
        }
    ]

    def diagnose(self, log_content: str) -> Dict[str, Any]:
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern["regex"], log_content, re.IGNORECASE):
                return {
                    "matched": True,
                    "error_id": pattern["id"],
                    "title": pattern["title"],
                    "root_cause": pattern["root_cause"],
                    "remediation": pattern["remediation"]
                }

        return {
            "matched": False,
            "error_id": "UNKNOWN_ERROR",
            "title": "General Pipeline Failure",
            "root_cause": "Log did not match known cloud infrastructure failure patterns.",
            "remediation": "Inspect full stdout/stderr stacktrace and verify provider authentication and permissions."
        }
