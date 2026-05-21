TOTAL_CALLS = 0


def increment_calls():

    global TOTAL_CALLS

    TOTAL_CALLS += 1


def get_cost_summary():

    return {
        "total_llm_calls": TOTAL_CALLS
    }