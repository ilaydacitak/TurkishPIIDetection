# TECHNICAL DESIGN DOCUMENT
# Context-Aware Synthetic PII Generation & Implicit Relation Labeling Strategy

**Date:** January 19, 2025
**Subject:** Methodology for PII Entity Classification and Contextual Noise Filtering
**Prepared For:** Academic Review

---

## 1. Executive Summary

This project proposes a novel, **hybrid architecture** for generating high-quality synthetic datasets aimed at Personally Identifiable Information (PII) extraction. Unlike traditional methods that focus solely on entity detection, this project addresses the **"Attribution Problem"** (distinguishing *whose* PII is present).

By utilizing **Gemini 1.5 Pro** as a creative architect and **Python (Faker)** as a deterministic builder, we aim to train a model that can differentiate between **Subject PII** (Target) and **Contextual Noise** (System/Employee metadata) without requiring complex relation extraction networks.

---

## 2. PII Taxonomy & Classification Logic

Entities are classified based on their **Identifiability** (power to identify a natural person alone) rather than their **Sensitivity**.

### 2.1. Classification Tiers
* **Strong (Direct Identifiers):** Entities that point directly to a unique individual without needing auxiliary data.
    * *Examples:* `SSN`, `Passport Number`, `Mobile Phone`, `Email Address`, `Biometric Data`.
* **Medium (Linkable / Pseudo-Identifiers):** Entities that single out an individual within a specific context or physical location but may not be globally unique identifiers.
    * *Examples:* `User ID`, `IP Address`, `Street Address`, `Device ID`, `Employee ID`.
* **Weak (Attributes / Quasi-Identifiers):** Attributes that are shared by many individuals but can lead to identification when combined (k-anonymity principle).
    * *Examples:* `First Name`, `Date of Birth`, `Gender`, `Zip Code`, `City`.

> **Note:** Critical security secrets like `Password` or `PIN` are treated as **Low Identifiability** (Weak) in this context, although they possess **High Sensitivity**.

---

## 3. Hybrid Data Generation Architecture

To overcome the limitations of LLMs (Safety Filters, Hallucinations) and ensure data consistency, a "Template Injection" pattern is adopted.

### 3.1. The Workflow: "Architect & Builder"

1.  **The Architect (Gemini 1.5 Pro):**
    * **Role:** Generates the unstructured text skeleton, narrative, and context.
    * **Mechanism:** Instead of generating fake data, it inserts strictly formatted placeholders.
    * **Output Example:** `"Patient {{WEAK__FIRST_NAME}} reported symptoms on {{WEAK__DATE}}."`
    * **Advantage:** Bypasses safety filters completely and ensures high linguistic variance.

2.  **The Builder (Python + Faker):**
    * **Role:** Fills placeholders with deterministic, format-controlled fake data.
    * **Mechanism:** Parses the template using Regex and maps tags to `Faker` (locale: `en_US`) functions.
    * **Advantage:** Generates **Perfect Ground Truth** labels automatically, eliminating human annotation errors.

---

## 4. Labeling Strategy: Implicit Relation Modeling

The project objective includes not just detecting PII, but determining if it belongs to the **Data Subject** (e.g., Patient) or **Contextual Noise** (e.g., Hospital Staff).

### 4.1. The Challenge
In an unstructured document, a phone number might belong to the patient or the attending nurse. Standard NER models cannot distinguish this context.

### 4.2. The Solution: Subject-Centric Annotation
Instead of building a separate "Relation Extraction" model, we embed the relation logic into the annotation phase.

* **Rule 1 (Subject PII):** If a placeholder is marked as `STRONG`, `MEDIUM`, or `WEAK` in the Subject Context, it is labeled with its entity type (e.g., `B-PHONE`).
* **Rule 2 (Contextual Noise):** If a placeholder is marked as `NOISE` (e.g., Employee ID, System Timestamp), it is **NOT labeled** (assigned `O` tag) or explicitly labeled as `NOISE_ENTITY`.

**Example:**
> Text: "Patient **Sarah** (`NAME`) called **555-0199** (`PHONE`). Logged by Admin ID: H-9921 (`O`)."

**Outcome:** The model learns implicitly that identifiers appearing in "administrative" contexts (headers, footers, log lines) are **not** the target PII, effectively filtering out noise without post-processing.

---

## 5. Technical Risks & Mitigations

| Risk | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Pattern Leakage** | The model memorizes the `Faker` library's specific formats (e.g., all phones starting with 555). | **High Variation Injection:** Use Python `random.choice()` to rotate between multiple formats (e.g., `(555) ...`, `555-...`, `+1 555...`). |
| **Hallucination** | The LLM might invent data instead of using placeholders. | **Strict System Prompts:** Use "Few-Shot Prompting" to enforce the `{{CATEGORY__TYPE}}` syntax rigorously. |
| **Locale Mismatch** | Date/Address formats may not match the target language region. | **Locale Enforcement:** Initialize Faker with `locale='en_US'` or the specific target region. |

---

## 6. Conclusion

This methodology provides a scalable, compliant, and cost-effective way to train robust PII detection models. By shifting the burden of "Relation Extraction" from the model architecture to the **Data Generation Strategy**, we achieve high performance on complex, unstructured documents with a simpler model inference pipeline.