
def contains_target_token(answer: str, target: str) -> bool:
    if not answer or not target:
        return False
    tokens = [t.strip(".,!?;:\"'()[]{}-") for t in answer.lower().split()]
    return target.lower() in tokens
