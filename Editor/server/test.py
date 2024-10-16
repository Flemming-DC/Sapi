from autotest.highlighter_test import test_tokenize, sqlglot_comment_format_test
from autotest.executor_test import test_code_actions


if __name__ == '__main__':
    sqlglot_comment_format_test()
    test_tokenize()
    test_code_actions()
    print("All Tests Passed")
        
