from test import execution_test, test_select, test_insert, demo_pg_model


if __name__ == '__main__':
    demo_pg_model.setup_db_and_make_datamodel()
    execution_test.run_tests()
    test_select.run_tests()
    test_insert.run_tests()
    print("All Tests Passed")
