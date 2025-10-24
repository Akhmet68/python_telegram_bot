def is_correct(user_answer: str, correct: str) -> bool:
    return user_answer.strip().lower() == str(correct).strip().lower()
