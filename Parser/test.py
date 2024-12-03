from test import execution_test, test_select, test_insert


if __name__ == '__main__':
    execution_test.run_tests()
    test_select.run_tests()
    test_insert.run_tests()
    print("All Tests Passed")
