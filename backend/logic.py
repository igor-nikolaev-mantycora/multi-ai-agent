from collections import Counter


def safe_answers(answers):
    clean = {}
    for name, value in answers.items():
        if value is None:
            continue
        text = str(value).strip()
        if text:
            clean[name] = text
    return clean


def normalize_text(value):
    return " ".join(str(value).strip().lower().split())


def split_sentences(text):
    cleaned = text.replace("\r", " ").replace("\n", " ")
    parts = [part.strip() for part in cleaned.split(".")]
    return [part for part in parts if part]


def extract_common_points(answers):
    counts = Counter()
    originals = {}

    for answer in answers.values():
        seen = set()
        for sentence in split_sentences(answer):
            normalized = normalize_text(sentence)
            if len(normalized) < 20 or normalized in seen:
                continue
            seen.add(normalized)
            counts[normalized] += 1
            originals.setdefault(normalized, sentence.strip())

    return [
        originals[key]
        for key, count in counts.most_common()
        if count >= 2
    ][:3]


def fallback_consensus(answers):
    if not answers:
        return {"answer": "No valid answers", "confidence": 0, "method": "no_answers"}

    grouped = {}
    for name, answer in answers.items():
        grouped.setdefault(normalize_text(answer), []).append((name, answer))

    common_points = extract_common_points(answers)
    largest_group = max(grouped.values(), key=len)

    if len(largest_group) >= 2:
        model_names = [name for name, _answer in largest_group]
        answer = largest_group[0][1]
        confidence = min(0.5 + (0.15 * (len(largest_group) - 1)), 0.85)
        return {
            "answer": answer,
            "confidence": round(confidence, 2),
            "method": "matching_answers",
            "agreeing_models": model_names,
            "common_points": common_points,
        }

    best_name, best_answer = max(answers.items(), key=lambda item: len(item[1]))
    return {
        "answer": best_answer,
        "confidence": 0.35 if len(answers) > 1 else 0.5,
        "method": "longest_answer",
        "selected_model": best_name,
        "common_points": common_points,
    }


def consensus(answers):
    answers = safe_answers(answers)
    if not answers:
        return {"error": "No valid answers"}
    return fallback_consensus(answers)


def contradictions(answers):
    answers = safe_answers(answers)
    if len(answers) < 2:
        return "Not enough data for contradiction analysis"

    grouped = {}
    for name, answer in answers.items():
        grouped.setdefault(normalize_text(answer), []).append(name)

    if len(grouped) <= 1:
        return "No clear contradictions detected"

    lines = []
    for normalized, names in list(grouped.items())[:4]:
        sample_name = names[0]
        excerpt = answers[sample_name][:220]
        lines.append(f"- {', '.join(names)}: {excerpt}")
    return "\n".join(lines)


def weighted_scores(answers):
    answers = safe_answers(answers)
    if not answers:
        return {"error": "No valid answers"}

    normalized_counts = Counter(normalize_text(answer) for answer in answers.values())
    scores = {}

    for name, answer in answers.items():
        normalized = normalize_text(answer)
        word_count = len(answer.split())
        sentence_count = max(len(split_sentences(answer)), 1)
        completeness = min(word_count / 80, 1.0)
        structure = min(sentence_count / 4, 1.0)
        agreement_bonus = 0.25 if normalized_counts[normalized] > 1 else 0.0

        quality = round((completeness * 6) + (structure * 2) + (agreement_bonus * 8), 2)
        confidence = round(min(0.25 + completeness * 0.3 + agreement_bonus, 0.95), 2)

        scores[name] = {
            "quality": min(quality, 10),
            "confidence": confidence,
        }

    return scores
