from .test_interpreter import stmt_test_template

def test_simple_if_then_no_else():
    stmt_test_template("""
    test <- true;
    if test {
      print 0;
    }
    """,
    ['0'])

def test_simple_if_then_with_else():
    stmt_test_template("""
    test <- true;
    if test {
      print 0;
    } else {
      print 1;
    }
    """,
    ['0'])

def test_integer_comparison():
    stmt_test_template("""
    x <- 12;
    if x == 9 + 3 {
      print 0;
    }
    """,
    ['0'])

def test_mixed_scope():
    stmt_test_template("""
    x <- 8;
    test <- true;
    if test {
      x <- x * 3;
    } else {
      x <- 0;
    }
    print x;
    """,
    ['24'])
