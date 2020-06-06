from .test_interpreter import stmt_test_template

def test_simple_scope():
    stmt_test_template("""
    u <- 0;
    {
      v <- 1;
      print v;
    }
    print u;
    """,
    ['1', '0'])

def test_mixed_scope():
    stmt_test_template("""
    x <- 7;
    {
      x <- x + 1;
    }
    print x;
    """,
    ['8'])

def test_complex_scope():
    stmt_test_template("""
    v <- 2;
    u <- 10;
    print u;
    {
      v <- 3;
      print v;
      {
        u <- u + v;
        {
          print u * 2;
        }
      }

      {
        u <- 0;
        print u;
      }
    }
    print v;
    """,
    ['10', '3', '26', '0', '3'])
