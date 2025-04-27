# Inputs

skills_list = """WebPAS (Patient Administration System)
EDIS (Emergency Department Information System)
Data entry
Medical records management
Digital medical record maintenance
Patient information management
Scanning and auditing records
Information retrieval systems
Keyboard proficiency"""

skills_array = skills_list.splitlines()
numbered_skills_str = "\n".join(f"{i}. {item}" for i, item in enumerate(skills_array, start=1))
start_bold = "\033[1m"
end_bold = "\033[0m"

print(numbered_skills_str)


# Prompt
print(f"""Okay, here is a prompt template you can use for Claude. You'll need to replace the bracketed placeholders `[...]` with your specific information.

---

**Prompt for Claude:**

**Your Role:** You are an expert resume writer and career coach specializing in optimizing resumes for Applicant Tracking Systems (ATS).

**Objective:** Rewrite my work experience section for my previous role as a `[Your Previous Role Title]` to make it highly ATS-compliant for a new job I am targeting. Your rewrite should seamlessly incorporate specific keywords, ensure every bullet point includes a quantifiable achievement, and consider my specific ideas for modifications.

**Input Information:**

1.  **My Previous Role:**
    `[Your Previous Role Title]`

2.  **My Original Work Experience (for the role above):**
    ```
    [Paste your original work experience bullet points here. Use bullet points or numbered lists.]
    ```

3.  **Target Job Information:**
    *(Please provide details about the new job you're applying for here. You can paste the job title, key responsibilities from the job description, or a general description of the type of role. This context is crucial for tailoring.)*
    `[Describe the target job or paste key requirements/responsibilities here]`

4.  **ATS-Friendly Keywords to Incorporate:**
    {numbered_skills_str}

5.  **My Ideas for Specific Modifications/Bullet Points:**
    *(These are the specific points you thought made sense)*
    ```
    [List your specific ideas for rewritten bullet points or concepts you want emphasized, e.g., "Focus on cost savings achieved through process optimization," "Highlight experience managing cross-functional teams," "Quantify client retention rate improvement."]
    ```

**Instructions for Claude:**

1.  **Analyze:** Review my original work experience, the target job information, the required keywords, and my specific ideas.
2.  **Rewrite for ATS:** Rephrase each bullet point using action verbs and language that is easily parsed by ATS software.
3.  **Integrate Keywords:** Naturally weave the provided `[List of Keywords]` into the rewritten bullet points where relevant. Avoid keyword stuffing; ensure they fit contextually.
4.  **Quantify Everything:** For *every* bullet point, add a specific, measurable result or quantifier. Use numbers, percentages, dollar amounts, timeframes, or scales (e.g., "managed a team of 5," "improved efficiency by 15%," "handled budgets up to $500k," "reduced project delivery time by 2 weeks," "increased customer satisfaction scores by 10 points"). If exact numbers aren't available from my original text, suggest realistic, plausible quantifiers based on the described task – clearly indicate these are suggestions if necessary (e.g., "potentially saving X hours/week" or "resulting in an estimated Y% increase").
5.  **Incorporate My Ideas:** Make sure to include or adapt the specific modifications and bullet point ideas I provided in section 5.
6.  **Format:** Present the final output as a list of bullet points suitable for a resume work experience section.
7.  **Focus:** Ensure the rewritten experience highlights skills and achievements most relevant to the `[Target Job Information]` provided.

**Output:**

Please provide the rewritten, ATS-optimized, and quantified work experience bullet points for my role as `[Your Previous Role Title]`.""")