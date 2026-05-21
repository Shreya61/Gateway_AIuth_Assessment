from app.evals.test_a_personal_finance_eval import run_test_a_eval
from app.evals.test_b_novella_eval import run_test_b_eval
from app.evals.test_c_tone_regeneration_eval import run_test_c_eval
from app.evals.test_d_insert_eval import run_test_d_eval


def main():
    print("TEST A")
    run_test_a_eval()
    print("TEST B")
    run_test_b_eval()
    print("TEST C")
    run_test_c_eval()
    print("TEST D")
    run_test_d_eval()


if __name__ == "__main__":
    main()
