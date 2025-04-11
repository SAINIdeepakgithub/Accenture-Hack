from autogen import AssistantAgent
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

matcher_agent = AssistantAgent(
    name="Matcher_Agent",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "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"}]},
    system_message="You compute match scores between job descriptions and parsed resumes."
)

@matcher_agent.register_for_execution()
def match_and_score(summary: dict):
    jd = summary.get("jd_summary", {})
    resumes = summary.get("parsed_resumes", [])
    threshold = summary.get("threshold", 80)

    results = []
    for res in resumes:
        jd_skill_text = ", ".join(jd.get("required_skills", []))
        res_skill_text = ", ".join(res.get("skills", []))

        jd_exp = " ".join(jd.get("experience", []))
        res_exp = " ".join(res.get("experience", []))

        jd_qual = " ".join(jd.get("qualifications", []))
        res_qual = " ".join(res.get("qualifications", []))

        jd_title = jd.get("job_title", "")
        res_title = res.get("job_title", "")

        skill_score = util.cos_sim(model.encode([jd_skill_text])[0], model.encode([res_skill_text])[0]).item()
        exp_score = util.cos_sim(model.encode([jd_exp])[0], model.encode([res_exp])[0]).item()
        qual_score = util.cos_sim(model.encode([jd_qual])[0], model.encode([res_qual])[0]).item()
        title_score = util.cos_sim(model.encode([jd_title])[0], model.encode([res_title])[0]).item()

        match_score = (0.5 * skill_score + 0.2 * exp_score + 0.2 * qual_score + 0.1 * title_score) * 100
        match_score = round(match_score, 2)
        status = "Shortlisted" if match_score >= threshold else "Rejected"

        res.update({"match_score": match_score, "status": status})
        results.append(res)

    summary["matched_resumes"] = results
    return summary
