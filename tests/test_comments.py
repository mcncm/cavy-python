from .test_interpreter import stmt_test_template

def test_simple_comment():
    stmt_test_template("""
    v <- 5;
    // ihtfp
    print v;
    """,
    ['5'])

def test_comment_with_assignment():
    stmt_test_template("""
    v <- 6;
    // foo; v <- 8
    print v;
    """,
    ['6'])

def test_comment_same_line():
    stmt_test_template("""
    v <- 7;  // yadda yadda yadda
    print v;
    """,
    ['7'])
