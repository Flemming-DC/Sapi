from autotest import highlighter_test, executor_test, hinting_test



if __name__ == '__main__':
    highlighter_test.sqlglot_comment_format_test()
    highlighter_test.test_tokenize()
    executor_test.test_code_actions()
    hinting_test.test_inlay_hints()
    print("All Tests Passed")
        
