

DOMAIN_CHUNKING_PROMPT = """
You are a cybersecurity policy analysis system.

Read the organizational policy text below and group the content
into the following FOUR domains:

1. Information Security Management System (ISMS)
2. Data Privacy and Security
3. Patch Management
4. Risk Management

Instructions:
- Assign each sentence or paragraph to the most relevant domain
- Combine all related content under the same domain
- Ensure that ALL policy text is assigned to exactly ONE domain
- Do not invent content
- If a domain is not mentioned, leave it empty
- Do not explain your reasoning

Allowed Subdomains (use exact wording):
- Acceptable Use Of Information Technology Resources Policy
- Access Control Policy
- Account Management Access Control
- Auditing And Accountability Policy
- Authentication Tokens
- Computer Security Threat Response Policy
- Configuration Management Policy
- Contingency Planning Policy
- Cyber Incident Response
- Encryption
- Identification And Authentication Policy
- Incident Response Policy
- Information Classification
- Information Security Policy
- Information Security Risk Management
- Maintenance Policy
- Media Protection Policy
- Mobile Device Security
- Patch Management
- Personnel Security Policy
- Physical And Environmental Protection Policy
- Planning Policy
- Remote Access
- Risk Assessment Policy
- Sanitization Secure Disposal
- Secure Configuration
- Secure System Development Life Cycle
- Security Assessment And Authorization Policy
- Security Awareness And Training Policy
- Security Logging
- System And Communications Protection Policy
- System And Information Integrity Policy
- System And Services Acquisition Policy
- Vulnerability Scanning

Policy Text:
{policy_text}

At the end, return the result as JSON in the following format:
{{
  "ISMS": {{
    "text": [],
    "subdomains": []
  }},
  "Data Privacy and Security": {{
    "text": [],
    "subdomains": []
  }},
  "Patch Management": {{
    "text": [],
    "subdomains": []
  }},
  "Risk Management": {{
    "text": [],
    "subdomains": []
  }}
}}
"""

GAP_ANALYSIS_PROMPT = """
You are a cybersecurity compliance auditor specializing in NIST framework alignment.

Your task is to analyze an organization's security policy and compare it against the
relevant NIST controls provided.

Domain: {domain}
Subdomain: {subdomain}

Organization Policy:
\"\"\"
{organization_policy}
\"\"\"

Relevant NIST Policy Extracts:
\"\"\"
{nist_chunks}
\"\"\"

Audit Guidelines:

- Compare the organization's policy with the provided NIST controls.
- Identify missing, incomplete, or weak controls.
- Policies that contain only general statements (e.g., "implement appropriate controls")
  should be treated as incomplete if specific procedures or mechanisms are not defined.
- A gap exists when the policy does not explicitly address a requirement present in the NIST controls.
- Do NOT invent gaps that are not supported by the comparison.

Tasks:

1. Identify all security gaps where the policy does not fully satisfy the NIST controls.
2. For each gap, reference the relevant NIST control when possible.
3. Provide improved policy statements that close the identified gaps.
4. Provide a practical remediation roadmap.

Output Rules:

- Return ONLY valid JSON.
- Do NOT include explanations outside JSON.
- If no gaps are found, return an empty "gap_analysis" list.
- If "gap_analysis" is empty, the roadmap sections should contain empty lists.

Output format:

{{
  "domain": "{domain}",
  "subdomain": "{subdomain}",
  "gap_analysis": [
    {{
      "gap_id": "GAP-001",
      "description": "Description of the missing or incomplete control",
      "nist_reference": "Relevant NIST control identifier",
      "severity": "High | Medium | Low",
      "impact": "Security or compliance impact"
    }}
  ],
  "revised_policy": {{
    "introduction": "Improved policy introduction aligned with NIST standards",
    "statements": [
      "Improved policy statement addressing the gap"
    ],
    "compliance_notes": "Explanation of how the improvements align with NIST"
  }},
  "implementation_roadmap": {{
    "short_term": [
      {{
        "action": "Immediate remediation action",
        "timeline": "0-3 months",
        "priority": "Critical | High | Medium | Low",
        "resources": "Required resources"
      }}
    ],
    "mid_term": [
      {{
        "action": "Medium-term improvement",
        "timeline": "3-6 months",
        "priority": "High | Medium",
        "resources": "Required resources"
      }}
    ],
    "long_term": [
      {{
        "action": "Long-term improvement",
        "timeline": "6-12 months",
        "priority": "Medium | Low",
        "resources": "Required resources"
      }}
    ]
  }}
}}
"""

GAP_ONLY_PROMPT = """
You are a cybersecurity compliance auditor specializing in NIST framework alignment.

Your task is to analyze an organization's security policy and identify gaps against the relevant NIST controls.

Domain: {domain}
Subdomain: {subdomain}

Organization Policy:
\"\"\"
{organization_policy}
\"\"\"

Relevant NIST Policy Extracts:
\"\"\"
{nist_chunks}
\"\"\"

Audit Guidelines:
- Compare the organization's policy with the provided NIST controls.
- Identify missing, incomplete, or weak controls.
- Policies with only general statements (e.g., "implement appropriate controls") should be treated as incomplete.
- A gap exists when the policy does not explicitly address a requirement present in the NIST controls.
- Do NOT invent gaps not supported by the comparison.

Output Rules:
- Return ONLY valid JSON.
- Do NOT include explanations outside JSON.
- If no gaps are found, return an empty "gap_analysis" list.

Output format:
{{
  "domain": "{domain}",
  "subdomain": "{subdomain}",
  "gap_analysis": [
    {{
      "gap_id": "GAP-001",
      "description": "Description of the missing or incomplete control",
      "nist_reference": "Relevant NIST control identifier",
      "severity": "High | Medium | Low",
      "impact": "Security or compliance impact"
    }}
  ]
}}
"""

REVISED_POLICY_PROMPT = """
You are a cybersecurity policy writer specializing in NIST framework alignment.

Your task is to generate a revised policy and implementation roadmap based on the identified gaps and the original organization policy.

Domain: {domain}
Subdomain: {subdomain}

Original Organization Policy:
\"\"\"
{organization_policy}
\"\"\"

Identified Gaps:
\"\"\"
{gap_analysis}
\"\"\"

Tasks:
1. Write improved policy statements that directly close each identified gap.
2. Provide a practical remediation roadmap with short, mid, and long-term actions.

Output Rules:
- Return ONLY valid JSON.
- Do NOT include explanations outside JSON.
- If gap_analysis is empty, return empty statements and roadmap lists.

Output format:
{{
  "domain": "{domain}",
  "subdomain": "{subdomain}",
  "revised_policy": {{
    "introduction": "Improved policy introduction aligned with NIST standards",
    "statements": [
      "Improved policy statement addressing each gap"
    ],
    "compliance_notes": "Explanation of how improvements align with NIST"
  }},
  "implementation_roadmap": {{
    "short_term": [
      {{
        "action": "Immediate remediation action",
        "timeline": "0-3 months",
        "priority": "Critical | High | Medium | Low",
        "resources": "Required resources"
      }}
    ],
    "mid_term": [
      {{
        "action": "Medium-term improvement",
        "timeline": "3-6 months",
        "priority": "High | Medium",
        "resources": "Required resources"
      }}
    ],
    "long_term": [
      {{
        "action": "Long-term improvement",
        "timeline": "6-12 months",
        "priority": "Medium | Low",
        "resources": "Required resources"
      }}
    ]
  }}
}}
"""